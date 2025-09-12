"""
Core data models for Doctor service
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from .enums import (
    DocumentFormat, TaskStatus, ConversionTheme, 
    CodeStyle, UploadSource, Priority, ErrorCode
)


# Custom types
def validate_file_size(v: int) -> int:
    """Validate file size"""
    from .enums import Constants
    if v <= 0:
        raise ValueError("File size must be positive")
    if v > Constants.MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds maximum of {Constants.MAX_FILE_SIZE} bytes")
    return v

def validate_file_path(v: str) -> str:
    """Validate file path"""
    path = Path(v)
    if path.is_absolute():
        raise ValueError("File path must be relative")
    if ".." in path.parts:
        raise ValueError("File path cannot contain parent directory references")
    return v

FileSize = Annotated[int, AfterValidator(validate_file_size)]
FilePath = Annotated[str, AfterValidator(validate_file_path)]


class ConversionOptions(BaseModel):
    """Options for document conversion"""
    
    theme: ConversionTheme = Field(
        default=ConversionTheme.DEFAULT,
        description="Visual theme for the converted document"
    )
    code_style: CodeStyle = Field(
        default=CodeStyle.DEFAULT,
        description="Syntax highlighting style for code blocks"
    )
    page_size: str = Field(
        default="A4",
        description="Page size for PDF output",
        pattern="^(A4|A3|Letter|Legal)$"
    )
    margin: str = Field(
        default="20mm",
        description="Page margins for PDF",
        pattern="^\\d+(mm|cm|in|px)$"
    )
    include_toc: bool = Field(
        default=False,
        description="Include table of contents"
    )
    include_page_numbers: bool = Field(
        default=True,
        description="Include page numbers in PDF"
    )
    embed_images: bool = Field(
        default=True,
        description="Embed images in the document"
    )
    process_math: bool = Field(
        default=True,
        description="Process LaTeX math expressions"
    )
    process_mermaid: bool = Field(
        default=True,
        description="Process Mermaid diagrams"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "theme": "github",
                "code_style": "monokai",
                "page_size": "A4",
                "include_toc": True
            }
        }
    )


class FileInfo(BaseModel):
    """Information about a file"""
    
    id: UUID = Field(default_factory=uuid4)
    filename: str = Field(..., min_length=1, max_length=255)
    format: DocumentFormat
    size: FileSize
    path: FilePath
    content_hash: str = Field(..., min_length=32, max_length=64)
    mime_type: str
    encoding: str = Field(default="utf-8")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate filename"""
        if not v or v.strip() != v:
            raise ValueError("Filename cannot be empty or contain leading/trailing spaces")
        
        # Check for invalid characters
        invalid_chars = ['/', '\\', '\0', '..']
        for char in invalid_chars:
            if char in v:
                raise ValueError(f"Filename cannot contain {char}")
        
        return v
    
    @field_validator('format', mode='before')
    @classmethod
    def normalize_format(cls, v: Any) -> DocumentFormat:
        """Normalize format value"""
        if isinstance(v, str):
            return DocumentFormat.normalize(v)
        return v
    
    @property
    def extension(self) -> str:
        """Get file extension"""
        return Path(self.filename).suffix.lower()
    
    def get_full_path(self, base_dir: Path) -> Path:
        """Get full file path"""
        return base_dir / self.path
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "document.md",
                "format": "markdown",
                "size": 1024,
                "path": "uploads/2024/01/document.md",
                "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "mime_type": "text/markdown"
            }
        }
    )


class Task(BaseModel):
    """Task model for conversion operations"""
    
    id: UUID = Field(default_factory=uuid4)
    status: TaskStatus = Field(default=TaskStatus.CREATED)
    priority: Priority = Field(default=Priority.NORMAL)
    source: UploadSource = Field(default=UploadSource.FILE)
    
    # File references
    input_file_id: UUID
    output_file_id: Optional[UUID] = None
    cache_key: Optional[str] = None
    
    # Conversion settings
    source_format: DocumentFormat
    target_format: DocumentFormat
    options: ConversionOptions = Field(default_factory=ConversionOptions)
    
    # Progress tracking
    progress: int = Field(default=0, ge=0, le=100)
    message: str = Field(default="Task created")
    error_code: Optional[ErrorCode] = None
    error_details: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Resource tracking
    processing_time: Optional[float] = None  # seconds
    memory_used: Optional[int] = None  # bytes
    retry_count: int = Field(default=0, ge=0, le=3)
    
    @field_validator('source_format', 'target_format')
    @classmethod
    def normalize_formats(cls, v: Any) -> DocumentFormat:
        """Normalize format values"""
        if isinstance(v, str):
            return DocumentFormat.normalize(v)
        return v
    
    @field_validator('target_format')
    @classmethod
    def validate_conversion(cls, v: DocumentFormat, info) -> DocumentFormat:
        """Validate that conversion is supported"""
        from .enums import Constants
        
        source = info.data.get('source_format')
        if source and not Constants.can_convert(source, v):
            raise ValueError(f"Cannot convert from {source} to {v}")
        return v
    
    @property
    def is_complete(self) -> bool:
        """Check if task is complete"""
        return self.status.is_final
    
    @property
    def is_active(self) -> bool:
        """Check if task is active"""
        return self.status.is_active
    
    @property
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.retry_count < 3 and self.status == TaskStatus.FAILED
    
    @property
    def duration(self) -> Optional[float]:
        """Get task duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def set_processing(self) -> None:
        """Set task as processing"""
        self.status = TaskStatus.PROCESSING
        self.started_at = datetime.utcnow()
        self.message = "Processing conversion"
    
    def set_completed(self, output_file_id: UUID) -> None:
        """Set task as completed"""
        self.status = TaskStatus.SUCCESS
        self.output_file_id = output_file_id
        self.completed_at = datetime.utcnow()
        self.progress = 100
        self.message = "Conversion completed successfully"
        
        if self.started_at:
            self.processing_time = (self.completed_at - self.started_at).total_seconds()
    
    def set_failed(self, error_code: ErrorCode, error_details: str) -> None:
        """Set task as failed"""
        self.status = TaskStatus.FAILED
        self.error_code = error_code
        self.error_details = error_details
        self.completed_at = datetime.utcnow()
        self.message = f"Conversion failed: {error_details}"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "processing",
                "source_format": "markdown",
                "target_format": "pdf",
                "progress": 50,
                "message": "Converting document..."
            }
        }
    )


class TaskStats(BaseModel):
    """Statistics for task execution"""
    
    total_tasks: int = Field(default=0, ge=0)
    active_tasks: int = Field(default=0, ge=0)
    queued_tasks: int = Field(default=0, ge=0)
    completed_tasks: int = Field(default=0, ge=0)
    failed_tasks: int = Field(default=0, ge=0)
    
    avg_processing_time: float = Field(default=0.0, ge=0.0)
    total_files_processed: int = Field(default=0, ge=0)
    total_bytes_processed: int = Field(default=0, ge=0)
    
    cache_hits: int = Field(default=0, ge=0)
    cache_misses: int = Field(default=0, ge=0)
    
    last_task_at: Optional[datetime] = None
    uptime_seconds: float = Field(default=0.0, ge=0.0)
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.completed_tasks + self.failed_tasks
        if total == 0:
            return 0.0
        return self.completed_tasks / total


class ConversionRequest(BaseModel):
    """Request model for document conversion"""
    
    file_id: UUID = Field(..., description="ID of the uploaded file")
    target_format: DocumentFormat = Field(..., description="Target document format")
    options: Optional[ConversionOptions] = Field(
        default=None,
        description="Conversion options"
    )
    priority: Priority = Field(
        default=Priority.NORMAL,
        description="Task priority"
    )
    
    @field_validator('target_format', mode='before')
    @classmethod
    def normalize_format(cls, v: Any) -> DocumentFormat:
        """Normalize format value"""
        if isinstance(v, str):
            return DocumentFormat.normalize(v)
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_id": "123e4567-e89b-12d3-a456-426614174000",
                "target_format": "pdf",
                "options": {
                    "theme": "github",
                    "include_toc": True
                }
            }
        }
    )


class FileUploadRequest(BaseModel):
    """Request model for file upload"""
    
    filename: str = Field(..., description="Name of the file")
    format: DocumentFormat = Field(..., description="Document format (user specified)")
    size: int = Field(..., gt=0, description="File size in bytes")
    
    @field_validator('format', mode='before')
    @classmethod
    def normalize_format(cls, v: Any) -> DocumentFormat:
        """Normalize format value"""
        if isinstance(v, str):
            return DocumentFormat.normalize(v)
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "document.txt",
                "format": "markdown",
                "size": 1024
            }
        }
    )


class ConversionResponse(BaseModel):
    """Response model for conversion request"""
    
    task_id: UUID = Field(..., description="ID of the created task")
    status: TaskStatus = Field(..., description="Current task status")
    message: str = Field(..., description="Status message")
    websocket_url: Optional[str] = Field(
        None,
        description="WebSocket URL for real-time updates"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "queued",
                "message": "Task queued for processing",
                "websocket_url": "ws://localhost:8000/ws/status/123e4567"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Error response model"""
    
    error_code: ErrorCode = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error_code": "file_too_large",
                "message": "File size exceeds maximum limit",
                "details": {
                    "max_size": 524288000,
                    "file_size": 600000000
                }
            }
        }
    )