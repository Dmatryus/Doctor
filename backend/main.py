"""
Doctor - Document Conversion Service
Main entry point
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.endpoints import upload, convert, preview, download
from app.api.websocket import status

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Doctor - Document Conversion Service",
    description="Convert documents between Markdown, PDF, and HTML formats",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(convert.router, prefix="/api/convert", tags=["convert"])
app.include_router(preview.router, prefix="/api/preview", tags=["preview"])
app.include_router(download.router, prefix="/api/download", tags=["download"])
app.include_router(status.router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Doctor",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development"
    )
