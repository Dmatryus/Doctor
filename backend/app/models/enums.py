"""
Enumerations and constants for Doctor service
"""

from enum import Enum
from typing import Set, Dict, List


class DocumentFormat(str, Enum):
    """Supported document formats"""
    MARKDOWN = "markdown"
    MD = "md"
    PDF = "pdf"
    HTML = "html"
    HTM = "htm"
    
    @classmethod
    def normalize(cls, format_str: str) -> 'DocumentFormat':
        """Normalize format string to enum value"""
        format_map = {
            "markdown": cls.MARKDOWN,
            "md": cls.MARKDOWN,
            "pdf": cls.PDF,
            "html": cls.HTML,
            "htm": cls.HTML,
        }
        return format_map.get(format_str.lower(), cls.MARKDOWN)
    
    @classmethod
    def get_extensions(cls) -> Set[str]:
        """Get all supported file extensions"""
        return {".md", ".markdown", ".pdf", ".html", ".htm"}
    
    @classmethod
    def from_extension(cls, extension: str) -> 'DocumentFormat':
        """Get format from file extension"""
        ext_map = {
            ".md": cls.MARKDOWN,
            ".markdown": cls.MARKDOWN,
            ".pdf": cls.PDF,
            ".html": cls.HTML,
            ".htm": cls.HTML,
        }
        return ext_map.get(extension.lower(), cls.MARKDOWN)
    
    def to_mime_type(self) -> str:
        """Get MIME type for format"""
        mime_map = {
            self.MARKDOWN: "text/markdown",
            self.MD: "text/markdown",
            self.PDF: "application/pdf",
            self.HTML: "text/html",
            self.HTM: "text/html",
        }
        return mime_map.get(self, "application/octet-stream")


class TaskStatus(str, Enum):
    """Task execution status"""
    CREATED = "created"
    QUEUED = "queued"
    WAITING = "waiting"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    
    @property
    def is_final(self) -> bool:
        """Check if status is final (no more changes expected)"""
        return self in {self.SUCCESS, self.FAILED, self.CANCELLED, self.EXPIRED}
    
    @property
    def is_active(self) -> bool:
        """Check if task is actively being processed"""
        return self == self.PROCESSING
    
    @property
    def can_cancel(self) -> bool:
        """Check if task can be cancelled"""
        return self in {self.CREATED, self.QUEUED, self.WAITING, self.PROCESSING}


class ConversionTheme(str, Enum):
    """Available conversion themes"""
    DEFAULT = "default"
    GITHUB = "github"
    MATERIAL = "material"
    DARK = "dark"
    LIGHT = "light"
    ACADEMIC = "academic"
    
    def get_css_url(self) -> str:
        """Get CSS URL for theme"""
        base_url = "/static/themes"
        return f"{base_url}/{self.value}.css"


class CodeStyle(str, Enum):
    """Code syntax highlighting styles"""
    DEFAULT = "default"
    MONOKAI = "monokai"
    GITHUB = "github"
    DRACULA = "dracula"
    SOLARIZED_LIGHT = "solarized-light"
    SOLARIZED_DARK = "solarized-dark"
    VS_CODE = "vs-code"
    ATOM_ONE = "atom-one"
    
    def get_highlight_class(self) -> str:
        """Get CSS class for highlighting"""
        return f"highlight-{self.value}"


class UploadSource(str, Enum):
    """Source of uploaded content"""
    FILE = "file"
    TEXT = "text"
    URL = "url"
    API = "api"


class Priority(int, Enum):
    """Task priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3
    
    @property
    def queue_weight(self) -> int:
        """Get queue weight for priority scheduling"""
        weights = {
            self.LOW: 1,
            self.NORMAL: 5,
            self.HIGH: 10,
            self.URGENT: 100,
        }
        return weights.get(self, 1)


class ErrorCode(str, Enum):
    """Error codes for API responses"""
    # File errors
    FILE_TOO_LARGE = "file_too_large"
    FILE_NOT_FOUND = "file_not_found"
    INVALID_FILE_FORMAT = "invalid_file_format"
    FILE_CORRUPTED = "file_corrupted"
    
    # Task errors
    TASK_NOT_FOUND = "task_not_found"
    TASK_EXPIRED = "task_expired"
    TASK_LIMIT_EXCEEDED = "task_limit_exceeded"
    TASK_TIMEOUT = "task_timeout"
    
    # Conversion errors
    CONVERSION_FAILED = "conversion_failed"
    UNSUPPORTED_CONVERSION = "unsupported_conversion"
    INVALID_OPTIONS = "invalid_options"
    
    # System errors
    STORAGE_ERROR = "storage_error"
    MEMORY_LIMIT = "memory_limit"
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    
    def to_http_status(self) -> int:
        """Get HTTP status code for error"""
        status_map = {
            self.FILE_TOO_LARGE: 413,
            self.FILE_NOT_FOUND: 404,
            self.INVALID_FILE_FORMAT: 400,
            self.FILE_CORRUPTED: 422,
            self.TASK_NOT_FOUND: 404,
            self.TASK_EXPIRED: 410,
            self.TASK_LIMIT_EXCEEDED: 429,
            self.TASK_TIMEOUT: 408,
            self.CONVERSION_FAILED: 500,
            self.UNSUPPORTED_CONVERSION: 400,
            self.INVALID_OPTIONS: 400,
            self.STORAGE_ERROR: 507,
            self.MEMORY_LIMIT: 507,
            self.INTERNAL_ERROR: 500,
            self.SERVICE_UNAVAILABLE: 503,
        }
        return status_map.get(self, 500)


class WebSocketEvent(str, Enum):
    """WebSocket event types"""
    CONNECTED = "connected"
    STATUS_UPDATE = "status_update"
    PROGRESS_UPDATE = "progress_update"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    ERROR = "error"
    DISCONNECTED = "disconnected"


# Constants
class Constants:
    """System-wide constants"""
    
    # File size limits (in bytes)
    MAX_FILE_SIZE = 524288000  # 500 MB
    MAX_TEXT_SIZE = 10485760   # 10 MB
    MAX_URL_SIZE = 104857600   # 100 MB
    
    # Task limits
    MAX_CONCURRENT_TASKS = 10
    MAX_TASKS_IN_MEMORY = 100
    MAX_TASKS_PER_USER = 5  # For future user-based limiting
    
    # Timeouts (in seconds)
    TASK_TIMEOUT = 300  # 5 minutes
    UPLOAD_TIMEOUT = 60  # 1 minute
    CONVERSION_TIMEOUT = 240  # 4 minutes
    CLEANUP_INTERVAL = 3600  # 1 hour
    
    # Cache settings
    CACHE_SIZE = 50  # Number of cached HTML files
    CACHE_TTL = 86400  # 24 hours
    
    # Preview settings
    PREVIEW_MAX_SIZE = 1048576  # 1 MB
    PREVIEW_IMAGE_WIDTH = 1200
    PREVIEW_IMAGE_HEIGHT = 1600
    
    # WebSocket settings
    WS_HEARTBEAT_INTERVAL = 30  # seconds
    WS_MAX_CONNECTIONS = 100
    
    # File paths (relative to project root)
    UPLOAD_DIR = "var/doctor/uploads"
    TEMP_DIR = "var/doctor/temp"
    CACHE_DIR = "var/doctor/cache"
    FILES_DIR = "var/doctor/files"
    PREVIEW_DIR = "var/doctor/preview"
    
    # Conversion matrix - what can be converted to what
    CONVERSION_MATRIX: Dict[DocumentFormat, List[DocumentFormat]] = {
        DocumentFormat.MARKDOWN: [DocumentFormat.PDF, DocumentFormat.HTML],
        DocumentFormat.PDF: [DocumentFormat.MARKDOWN, DocumentFormat.HTML],
        DocumentFormat.HTML: [DocumentFormat.MARKDOWN, DocumentFormat.PDF],
    }
    
    @classmethod
    def can_convert(cls, source: DocumentFormat, target: DocumentFormat) -> bool:
        """Check if conversion is supported"""
        source_norm = DocumentFormat.normalize(source.value)
        target_norm = DocumentFormat.normalize(target.value)
        
        if source_norm == target_norm:
            return False
            
        return target_norm in cls.CONVERSION_MATRIX.get(source_norm, [])