"""
Custom exceptions for Doctor service
"""

from typing import Any, Dict, Optional
from uuid import UUID

from ..models.enums import ErrorCode


class DoctorException(Exception):
    """Base exception for all Doctor service errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[ErrorCode] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or ErrorCode.INTERNAL_ERROR
        self.details = details or {}
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }


class ValidationError(DoctorException):
    """Validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = {"field": field} if field else {}
        details.update(kwargs)
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_FILE_FORMAT,
            details=details,
            status_code=400
        )


class FileError(DoctorException):
    """File-related errors"""
    pass


class FileNotFoundError(FileError):
    """File not found error"""
    
    def __init__(self, file_id: Optional[UUID] = None, filename: Optional[str] = None):
        if file_id:
            message = f"File with ID {file_id} not found"
            details = {"file_id": str(file_id)}
        elif filename:
            message = f"File '{filename}' not found"
            details = {"filename": filename}
        else:
            message = "File not found"
            details = {}
        
        super().__init__(
            message=message,
            error_code=ErrorCode.FILE_NOT_FOUND,
            details=details,
            status_code=404
        )


class FileTooLargeError(FileError):
    """File too large error"""
    
    def __init__(self, size: int, max_size: int):
        super().__init__(
            message=f"File size {size} bytes exceeds maximum of {max_size} bytes",
            error_code=ErrorCode.FILE_TOO_LARGE,
            details={"size": size, "max_size": max_size},
            status_code=413
        )


class FileCorruptedError(FileError):
    """File corrupted error"""
    
    def __init__(self, filename: str, reason: str):
        super().__init__(
            message=f"File '{filename}' is corrupted: {reason}",
            error_code=ErrorCode.FILE_CORRUPTED,
            details={"filename": filename, "reason": reason},
            status_code=422
        )


class TaskError(DoctorException):
    """Task-related errors"""
    pass


class TaskNotFoundError(TaskError):
    """Task not found error"""
    
    def __init__(self, task_id: UUID):
        super().__init__(
            message=f"Task with ID {task_id} not found",
            error_code=ErrorCode.TASK_NOT_FOUND,
            details={"task_id": str(task_id)},
            status_code=404
        )


class TaskExpiredError(TaskError):
    """Task expired error"""
    
    def __init__(self, task_id: UUID):
        super().__init__(
            message=f"Task with ID {task_id} has expired",
            error_code=ErrorCode.TASK_EXPIRED,
            details={"task_id": str(task_id)},
            status_code=410
        )


class TaskLimitExceededError(TaskError):
    """Task limit exceeded error"""
    
    def __init__(self, current_count: int, max_count: int):
        super().__init__(
            message=f"Task limit exceeded: {current_count}/{max_count} tasks active",
            error_code=ErrorCode.TASK_LIMIT_EXCEEDED,
            details={"current_count": current_count, "max_count": max_count},
            status_code=429
        )


class TaskTimeoutError(TaskError):
    """Task timeout error"""
    
    def __init__(self, task_id: UUID, timeout: int):
        super().__init__(
            message=f"Task {task_id} timed out after {timeout} seconds",
            error_code=ErrorCode.TASK_TIMEOUT,
            details={"task_id": str(task_id), "timeout": timeout},
            status_code=408
        )


class ConversionError(DoctorException):
    """Conversion-related errors"""
    pass


class ConversionFailedError(ConversionError):
    """Conversion failed error"""
    
    def __init__(self, source_format: str, target_format: str, reason: str):
        super().__init__(
            message=f"Conversion from {source_format} to {target_format} failed: {reason}",
            error_code=ErrorCode.CONVERSION_FAILED,
            details={
                "source_format": source_format,
                "target_format": target_format,
                "reason": reason
            },
            status_code=500
        )


class UnsupportedConversionError(ConversionError):
    """Unsupported conversion error"""
    
    def __init__(self, source_format: str, target_format: str):
        super().__init__(
            message=f"Conversion from {source_format} to {target_format} is not supported",
            error_code=ErrorCode.UNSUPPORTED_CONVERSION,
            details={"source_format": source_format, "target_format": target_format},
            status_code=400
        )


class InvalidOptionsError(ConversionError):
    """Invalid conversion options error"""
    
    def __init__(self, message: str, option_name: Optional[str] = None):
        details = {"option_name": option_name} if option_name else {}
        super().__init__(
            message=f"Invalid conversion options: {message}",
            error_code=ErrorCode.INVALID_OPTIONS,
            details=details,
            status_code=400
        )


class StorageError(DoctorException):
    """Storage-related errors"""
    
    def __init__(self, message: str, operation: str):
        super().__init__(
            message=f"Storage error during {operation}: {message}",
            error_code=ErrorCode.STORAGE_ERROR,
            details={"operation": operation},
            status_code=507
        )


class MemoryLimitError(DoctorException):
    """Memory limit exceeded error"""
    
    def __init__(self, current_usage: int, max_usage: int):
        super().__init__(
            message=f"Memory limit exceeded: {current_usage} > {max_usage} bytes",
            error_code=ErrorCode.MEMORY_LIMIT,
            details={"current_usage": current_usage, "max_usage": max_usage},
            status_code=507
        )


class ServiceUnavailableError(DoctorException):
    """Service unavailable error"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Service unavailable: {reason}",
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            details={"reason": reason},
            status_code=503
        )


# Convenience functions for creating common exceptions
def file_not_found(file_id: Optional[UUID] = None, filename: Optional[str] = None) -> FileNotFoundError:
    """Create a file not found exception"""
    return FileNotFoundError(file_id=file_id, filename=filename)


def file_too_large(size: int, max_size: int) -> FileTooLargeError:
    """Create a file too large exception"""
    return FileTooLargeError(size=size, max_size=max_size)


def task_not_found(task_id: UUID) -> TaskNotFoundError:
    """Create a task not found exception"""
    return TaskNotFoundError(task_id=task_id)


def conversion_failed(source_format: str, target_format: str, reason: str) -> ConversionFailedError:
    """Create a conversion failed exception"""
    return ConversionFailedError(source_format=source_format, target_format=target_format, reason=reason)


def unsupported_conversion(source_format: str, target_format: str) -> UnsupportedConversionError:
    """Create an unsupported conversion exception"""
    return UnsupportedConversionError(source_format=source_format, target_format=target_format)