"""
Data validators for Doctor service

Minimalist approach to validation:
- Security checks only (path traversal, XSS, etc.)
- No format detection or content analysis
- User specifies format explicitly
- Converters handle format validation at runtime
"""

import re
import hashlib
import ipaddress
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

from .enums import DocumentFormat, Constants


class FileValidator:
    """
    File validation focused on security, not format detection.
    Any file extension is acceptable - user specifies the format.
    """
    
    @classmethod
    def validate_filename(cls, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate filename for security risks only.
        Does NOT validate file extensions or format.
        
        Args:
            filename: Name of the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "Filename cannot be empty"
        
        # Security: Check for path traversal attempts
        if ".." in filename or "/" in filename or "\\" in filename:
            return False, "Filename contains path traversal characters"
        
        # Security: Check for null bytes
        if "\0" in filename:
            return False, "Filename contains null bytes"
        
        # Practical: Check length
        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"
        
        # Security: Check for dangerous characters (XSS, command injection)
        if re.search(r'[<>:"|?*]', filename):
            return False, "Filename contains potentially dangerous characters"
        
        return True, None
    
    @classmethod
    def validate_file_size(cls, size: int, source: str = "file") -> Tuple[bool, Optional[str]]:
        """
        Validate file size based on source type.
        
        Args:
            size: File size in bytes
            source: Source type (file, text, url)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if size <= 0:
            return False, "File size must be positive"
        
        # Different limits for different sources
        max_sizes = {
            "file": Constants.MAX_FILE_SIZE,      # 500 MB
            "text": Constants.MAX_TEXT_SIZE,      # 10 MB
            "url": Constants.MAX_URL_SIZE,        # 100 MB
        }
        
        max_size = max_sizes.get(source, Constants.MAX_FILE_SIZE)
        
        if size > max_size:
            return False, f"Size {size} bytes exceeds maximum of {max_size} bytes"
        
        return True, None
    
    @classmethod
    def quick_format_check(cls, file_path: Path, expected_format: DocumentFormat) -> Tuple[bool, Optional[str]]:
        """
        Optional quick sanity check - NOT comprehensive validation.
        Only checks obvious issues (e.g., PDF header).
        Real validation happens in converters.
        
        Args:
            file_path: Path to the file
            expected_format: Format claimed by user
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path.exists():
            return False, "File does not exist"
        
        try:
            with open(file_path, 'rb') as f:
                # Read first 1KB for quick check
                header = f.read(1024)
                
                # Only check PDF - it has a reliable header
                if expected_format == DocumentFormat.PDF:
                    if not header.startswith(b'%PDF'):
                        return False, "File doesn't appear to be a PDF (missing %PDF header)"
                
                # For text formats, just check it's not obviously binary
                elif expected_format in [DocumentFormat.HTML, DocumentFormat.HTM, 
                                       DocumentFormat.MARKDOWN, DocumentFormat.MD]:
                    # Check for null bytes (indicates binary file)
                    if b'\x00' in header:
                        return False, "File appears to be binary, not text"
                    
                    # Try to decode as text (any encoding is OK)
                    try:
                        header.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            header.decode('latin-1')
                        except:
                            return False, "File is not readable as text"
            
            return True, None
            
        except Exception:
            # If we can't read the file, let the converter handle it
            return True, None  # Optimistic approach
    
    @classmethod
    def calculate_hash(cls, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file content.
        
        Args:
            file_path: Path to the file
            
        Returns:
            64-character hex string of SHA256 hash
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks for memory efficiency
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @classmethod
    def sanitize_path(cls, path: str) -> str:
        """
        Sanitize file path for secure storage.
        Converts to relative path, removes parent references.
        
        Args:
            path: Input path string
            
        Returns:
            Sanitized relative path
        """
        p = Path(path)
        
        # If absolute or has parent references, just use filename
        if p.is_absolute() or '..' in p.parts:
            return p.name
        
        # Convert to forward slashes for consistency
        return str(p).replace('\\', '/')


class URLValidator:
    """
    URL validation for security.
    Blocks local/private addresses and dangerous schemes.
    """
    
    ALLOWED_SCHEMES = {'http', 'https'}
    BLOCKED_DOMAINS = {'localhost', '127.0.0.1', '0.0.0.0', '::1'}
    
    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate URL for security risks.
        
        Args:
            url: URL string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL cannot be empty"
        
        if len(url) > 2048:
            return False, "URL too long (max 2048 characters)"
        
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in cls.ALLOWED_SCHEMES:
                return False, f"URL scheme '{parsed.scheme}' not allowed (use http/https)"
            
            # Check for local addresses
            if parsed.hostname in cls.BLOCKED_DOMAINS:
                return False, "Cannot access localhost"
            
            # Check for private IP addresses
            if parsed.hostname and cls._is_private_ip(parsed.hostname):
                return False, "Cannot access private network addresses"
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid URL: {str(e)}"
    
    @staticmethod
    def _is_private_ip(hostname: str) -> bool:
        """Check if hostname is a private IP address."""
        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_private or ip.is_reserved or ip.is_loopback
        except ValueError:
            # Not an IP address (probably domain name)
            return False


class TextValidator:
    """
    Text validation - minimal approach.
    No format-specific validation, just basic security.
    """
    
    @classmethod
    def validate_text_input(cls, text: str, max_size: int = None) -> Tuple[bool, Optional[str]]:
        """
        Basic validation for text input.
        
        Args:
            text: Text content
            max_size: Maximum size in bytes (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return False, "Text cannot be empty"
        
        # Security: Check for null bytes
        if '\0' in text:
            return False, "Text contains null bytes"
        
        # Size check if specified
        if max_size:
            text_bytes = text.encode('utf-8')
            if len(text_bytes) > max_size:
                return False, f"Text size {len(text_bytes)} bytes exceeds maximum of {max_size} bytes"
        
        return True, None
    
    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """
        Basic text sanitization.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text
        """
        # Remove null bytes
        text = text.replace('\0', '')
        
        # Normalize line endings to Unix style
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        return text


class ConversionValidator:
    """
    Conversion validation - checks if conversion is supported.
    Minimal validation of options.
    """
    
    @classmethod
    def validate_conversion(cls, source_format: DocumentFormat, target_format: DocumentFormat) -> Tuple[bool, Optional[str]]:
        """
        Check if conversion from source to target format is supported.
        
        Args:
            source_format: Source document format
            target_format: Target document format
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Normalize formats (handle both enum and string)
        if hasattr(source_format, 'value'):
            source_str = source_format.value
        else:
            source_str = str(source_format)
        
        if hasattr(target_format, 'value'):
            target_str = target_format.value
        else:
            target_str = str(target_format)
        
        source_norm = DocumentFormat.normalize(source_str)
        target_norm = DocumentFormat.normalize(target_str)
        
        # Can't convert to same format
        if source_norm == target_norm:
            return False, "Source and target formats are the same"
        
        # Check conversion matrix
        if not Constants.can_convert(source_norm, target_norm):
            return False, f"Conversion from {source_norm.value} to {target_norm.value} is not supported"
        
        return True, None
    
    @classmethod
    def validate_conversion_options(cls, options: dict) -> Tuple[bool, Optional[str]]:
        """
        Basic validation of conversion options.
        Only validates critical options, not themes or styles.
        
        Args:
            options: Dictionary of conversion options
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not options:
            return True, None  # Empty options are OK
        
        # Validate page size if specified
        if 'page_size' in options:
            valid_sizes = ['A4', 'A3', 'Letter', 'Legal']
            if options['page_size'] not in valid_sizes:
                return False, f"Invalid page size: {options['page_size']}"
        
        # Validate margin format if specified
        if 'margin' in options:
            margin = options['margin']
            # Must be string
            if not isinstance(margin, str):
                return False, "Margin must be a string (e.g., '20mm')"
            # Must match pattern: number + unit
            if not re.match(r'^\d+(mm|cm|in|px)$', margin):
                return False, f"Invalid margin format: {margin} (use format like '20mm')"
        
        return True, None