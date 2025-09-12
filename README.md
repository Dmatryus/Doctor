# Doctor - Document Conversion Service

## Overview
Web service for converting documents between Markdown, PDF, and HTML formats.

## Features
- Support for Markdown, PDF, and HTML formats
- Drag & drop file upload
- Real-time conversion status via WebSocket
- Preview before download
- Theme customization
- Syntax highlighting for code blocks

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
flutter pub get
flutter run -d chrome
```

## Architecture
- Backend: FastAPI + Python
- Frontend: Flutter Web
- Conversion: HTML as universal intermediate format
- Storage: In-memory tasks + filesystem for files
- Monitoring: Prometheus + Grafana

## Documentation
See `/docs` directory for detailed documentation.
