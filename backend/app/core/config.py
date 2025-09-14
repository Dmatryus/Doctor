"""
Configuration management for Doctor service
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    APP_NAME: str = Field(default="Doctor", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version") 
    APP_ENV: str = Field(default="development", description="Environment: development, production")
    APP_HOST: str = Field(default="0.0.0.0", description="Host to bind to")
    APP_PORT: int = Field(default=8000, description="Port to bind to")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    
    # CORS settings  
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials in CORS")
    
    # File storage settings
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent.parent)
    STORAGE_ROOT: Path = Field(default=Path("var/doctor"), description="Root storage directory")
    UPLOAD_DIR: Path = Field(default=Path("var/doctor/uploads"), description="Upload directory")
    TEMP_DIR: Path = Field(default=Path("var/doctor/temp"), description="Temporary directory")
    CACHE_DIR: Path = Field(default=Path("var/doctor/cache"), description="Cache directory")
    FILES_DIR: Path = Field(default=Path("var/doctor/files"), description="Files directory") 
    PREVIEW_DIR: Path = Field(default=Path("var/doctor/preview"), description="Preview directory")
    LOGS_DIR: Path = Field(default=Path("var/doctor/logs"), description="Logs directory")
    
    # File size limits (bytes)
    MAX_FILE_SIZE: int = Field(default=524288000, description="Max file size: 500MB")
    MAX_TEXT_SIZE: int = Field(default=10485760, description="Max text size: 10MB")
    MAX_URL_SIZE: int = Field(default=104857600, description="Max URL download size: 100MB")
    
    # Task management
    MAX_CONCURRENT_TASKS: int = Field(default=10, description="Maximum concurrent tasks")
    MAX_TASKS_IN_MEMORY: int = Field(default=100, description="Maximum tasks in memory")
    TASK_TIMEOUT: int = Field(default=300, description="Task timeout in seconds (5 min)")
    CLEANUP_INTERVAL: int = Field(default=3600, description="Cleanup interval in seconds (1 hour)")
    
    # Cache settings
    CACHE_SIZE: int = Field(default=50, description="Number of cached HTML files")
    CACHE_TTL: int = Field(default=86400, description="Cache TTL in seconds (24 hours)")
    
    # WebSocket settings
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, description="WebSocket heartbeat interval")
    WS_MAX_CONNECTIONS: int = Field(default=100, description="Maximum WebSocket connections")
    
    # Security settings
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", description="Secret key")
    ALLOW_ORIGINS: List[str] = Field(default=["*"], description="Allowed origins")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    LOG_TO_FILE: bool = Field(default=True, description="Enable file logging")
    LOG_ROTATION: bool = Field(default=True, description="Enable log rotation")
    LOG_MAX_SIZE: str = Field(default="10MB", description="Maximum log file size")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Number of backup log files")
    
    # Monitoring settings
    PROMETHEUS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics")
    PROMETHEUS_PORT: int = Field(default=9090, description="Prometheus port")
    
    # External services settings
    WKHTMLTOPDF_PATH: Optional[str] = Field(
        default=None, 
        description="Path to wkhtmltopdf binary (auto-detected if None)"
    )
    
    @validator('APP_ENV')
    def validate_env(cls, v):
        """Validate environment value"""
        valid_envs = ['development', 'testing', 'production']
        if v not in valid_envs:
            raise ValueError(f'APP_ENV must be one of: {valid_envs}')
        return v
    
    @validator('LOG_LEVEL')  
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of: {valid_levels}')
        return v_upper
        
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.APP_ENV == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.APP_ENV == "production"
    
    @property
    def storage_paths(self) -> dict:
        """Get all storage paths as absolute paths"""
        base = Path.cwd()
        return {
            'upload': base / self.UPLOAD_DIR,
            'temp': base / self.TEMP_DIR, 
            'cache': base / self.CACHE_DIR,
            'files': base / self.FILES_DIR,
            'preview': base / self.PREVIEW_DIR,
            'logs': base / self.LOGS_DIR,
        }
    
    def create_directories(self) -> None:
        """Create all required directories"""
        for path in self.storage_paths.values():
            path.mkdir(parents=True, exist_ok=True)
            
    def get_file_path(self, file_type: str, filename: str) -> Path:
        """Get full path for a file of specific type"""
        paths = self.storage_paths
        if file_type not in paths:
            raise ValueError(f"Unknown file type: {file_type}")
        return paths[file_type] / filename
    
    class Config:
        """Pydantic settings configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        # Environment variable prefixes
        env_prefix = ""
        
        # Example values for documentation
        schema_extra = {
            "example": {
                "APP_ENV": "production",
                "APP_PORT": 8000,
                "MAX_CONCURRENT_TASKS": 10,
                "LOG_LEVEL": "INFO"
            }
        }


# Create global settings instance
settings = Settings()

# Ensure directories exist on import
settings.create_directories()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment"""
    global settings
    settings = Settings()
    settings.create_directories()
    return settings