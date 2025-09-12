#!/usr/bin/env python3
"""
Test the cleaned validators - no magic, no complex logic
Just security and basic sanity checks
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.app.models.validators import (
    FileValidator, URLValidator, TextValidator, ConversionValidator
)
from backend.app.models.enums import DocumentFormat, Constants


def test_file_validator():
    """Test FileValidator - security focus only"""
    print("=" * 60)
    print("Testing FileValidator (Security Focus)")
    print("=" * 60)
    
    print("\n1️⃣ Filename validation (security only):")
    test_cases = [
        ("report.md", True, "Normal filename"),
        ("file.xyz", True, "Unknown extension - OK"),
        ("no_extension", True, "No extension - OK"),
        ("файл.txt", True, "Unicode - OK"),
        ("very-long-name.pdf", True, "Long name - OK"),
        
        # Security issues
        ("../../../etc/passwd", False, "Path traversal"),
        ("file\0name.txt", False, "Null byte"),
        ("file/with/slash.txt", False, "Path separator"),
        ("file\\with\\backslash.txt", False, "Windows path"),
        ("file<script>.html", False, "XSS characters"),
    ]
    
    for filename, should_pass, description in test_cases:
        is_valid, error = FileValidator.validate_filename(filename)
        status = "✅" if is_valid == should_pass else "❌"
        print(f"  {status} {description:20} - {filename}")
        if not is_valid and should_pass:
            print(f"      ERROR: {error}")
    
    print("\n2️⃣ File size validation:")
    test_cases = [
        (1024, "file", True, "1KB file"),
        (500_000_000, "file", True, "500MB file - max"),
        (500_000_001, "file", False, "Over 500MB"),
        (10_000_000, "text", True, "10MB text - max"),
        (10_000_001, "text", False, "Over 10MB text"),
    ]
    
    for size, source, should_pass, description in test_cases:
        is_valid, error = FileValidator.validate_file_size(size, source)
        status = "✅" if is_valid == should_pass else "❌"
        print(f"  {status} {description}")
    
    print("\n3️⃣ Quick format check (optional):")
    
    # Test PDF
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(b'%PDF-1.4\n')
        pdf_path = Path(f.name)
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(b'Not a PDF')
        fake_pdf_path = Path(f.name)
    
    try:
        is_valid, _ = FileValidator.quick_format_check(pdf_path, DocumentFormat.PDF)
        print(f"  {'✅' if is_valid else '❌'} Real PDF with %PDF header")
        
        is_valid, _ = FileValidator.quick_format_check(fake_pdf_path, DocumentFormat.PDF)
        print(f"  {'✅' if not is_valid else '❌'} Fake PDF without header")
        
        # Text formats - should pass if not binary
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Some text content")
            text_path = Path(f.name)
        
        is_valid, _ = FileValidator.quick_format_check(text_path, DocumentFormat.MARKDOWN)
        print(f"  {'✅' if is_valid else '❌'} Text file as Markdown")
        
        text_path.unlink()
    finally:
        pdf_path.unlink()
        fake_pdf_path.unlink()
    
    print("\n4️⃣ Path sanitization:")
    test_paths = [
        ("uploads/file.txt", "uploads/file.txt"),
        ("uploads\\file.txt", "uploads/file.txt"),  # Windows to Unix
        ("/absolute/path/file.txt", "file.txt"),  # Absolute to filename
        ("../../../file.txt", "file.txt"),  # Parent refs to filename
        ("uploads/../file.txt", "file.txt"),  # Complex path to filename
    ]
    
    for input_path, expected in test_paths:
        result = FileValidator.sanitize_path(input_path)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {input_path:25} → {result}")


def test_url_validator():
    """Test URLValidator - security focus"""
    print("\n" + "=" * 60)
    print("Testing URLValidator")
    print("=" * 60)
    
    test_cases = [
        ("https://example.com", True, "Valid HTTPS"),
        ("http://example.com", True, "Valid HTTP"),
        ("https://example.com/path?query=1", True, "With path and query"),
        
        ("ftp://example.com", False, "Wrong scheme"),
        ("javascript:alert(1)", False, "XSS attempt"),
        ("http://localhost/admin", False, "Localhost blocked"),
        ("http://127.0.0.1:8080", False, "Local IP blocked"),
        ("http://192.168.1.1", False, "Private IP blocked"),
        ("https://" + "x" * 2040, False, "Too long URL"),
    ]
    
    for url, should_pass, description in test_cases:
        is_valid, error = URLValidator.validate_url(url)
        status = "✅" if is_valid == should_pass else "❌"
        print(f"  {status} {description:20} - {url[:50]}")


def test_text_validator():
    """Test TextValidator - simplified"""
    print("\n" + "=" * 60)
    print("Testing TextValidator (Simplified)")
    print("=" * 60)
    
    print("\n1️⃣ Basic text validation:")
    test_cases = [
        ("Hello World", None, True, "Normal text"),
        ("", None, False, "Empty text"),
        ("Hello\0World", None, False, "Null byte"),
        ("Small", 100, True, "Under size limit"),
        ("x" * 1000, 100, False, "Over size limit"),
    ]
    
    for text, max_size, should_pass, description in test_cases:
        is_valid, error = TextValidator.validate_text_input(text, max_size)
        status = "✅" if is_valid == should_pass else "❌"
        print(f"  {status} {description}")
    
    print("\n2️⃣ Text sanitization:")
    test_cases = [
        ("Hello\0World", "HelloWorld", "Remove null bytes"),
        ("Line1\r\nLine2", "Line1\nLine2", "Normalize CRLF"),
        ("Line1\rLine2", "Line1\nLine2", "Normalize CR"),
        ("Normal text", "Normal text", "No change needed"),
    ]
    
    for input_text, expected, description in test_cases:
        result = TextValidator.sanitize_text(input_text)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {description}")


def test_conversion_validator():
    """Test ConversionValidator - simplified"""
    print("\n" + "=" * 60)
    print("Testing ConversionValidator (Simplified)")
    print("=" * 60)
    
    print("\n1️⃣ Conversion support:")
    test_cases = [
        (DocumentFormat.MARKDOWN, DocumentFormat.PDF, True, "MD → PDF"),
        (DocumentFormat.PDF, DocumentFormat.HTML, True, "PDF → HTML"),
        (DocumentFormat.HTML, DocumentFormat.MARKDOWN, True, "HTML → MD"),
        (DocumentFormat.PDF, DocumentFormat.PDF, False, "Same format"),
        (DocumentFormat.MARKDOWN, DocumentFormat.MARKDOWN, False, "Same format"),
    ]
    
    for source, target, should_support, description in test_cases:
        is_valid, error = ConversionValidator.validate_conversion(source, target)
        status = "✅" if is_valid == should_support else "❌"
        print(f"  {status} {description}")
    
    print("\n2️⃣ Conversion options validation:")
    test_options = [
        ({"page_size": "A4"}, True, "Valid page size"),
        ({"page_size": "X5"}, False, "Invalid page size"),
        ({"margin": "20mm"}, True, "Valid margin"),
        ({"margin": "20"}, False, "Invalid margin format"),
        ({"margin": 20}, False, "Wrong margin type"),
        ({}, True, "Empty options OK"),
    ]
    
    for options, should_pass, description in test_options:
        is_valid, error = ConversionValidator.validate_conversion_options(options)
        status = "✅" if is_valid == should_pass else "❌"
        print(f"  {status} {description}")
        if not is_valid and should_pass:
            print(f"      ERROR: {error}")


def test_minimalist_philosophy():
    """Demonstrate the minimalist philosophy"""
    print("\n" + "=" * 60)
    print("Minimalist Philosophy in Action")
    print("=" * 60)
    
    print("\n📝 What we DON'T do anymore:")
    print("  ❌ No MIME type detection")
    print("  ❌ No magic bytes analysis") 
    print("  ❌ No extension validation")
    print("  ❌ No complex content parsing")
    print("  ❌ No format guessing")
    
    print("\n✅ What we DO:")
    print("  ✅ Security checks (path traversal, XSS, etc.)")
    print("  ✅ Size validation")
    print("  ✅ Quick sanity check (PDF header only)")
    print("  ✅ Trust user's format specification")
    print("  ✅ Let converters handle format errors")
    
    print("\n🎯 Result:")
    print("  • Simpler code (~200 lines vs ~500)")
    print("  • No external dependencies")
    print("  • No false positives")
    print("  • Clear error messages from converters")
    print("  • User learns correct format through feedback")


def main():
    """Run all tests"""
    print("\n🧪 Clean Validators Test Suite")
    print("=" * 60)
    print("Testing minimalist validation approach")
    print("No magic, no complex logic, just security")
    print("=" * 60)
    
    test_file_validator()
    test_url_validator()
    test_text_validator()
    test_conversion_validator()
    test_minimalist_philosophy()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\nThe validators are now:")
    print("• Simpler - less code to maintain")
    print("• Cleaner - no external dependencies")
    print("• Focused - security over format detection")
    print("• Pragmatic - trust users, fail clearly")


if __name__ == "__main__":
    main()