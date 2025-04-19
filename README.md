# File Size Reducer

A Flask web application for reducing the size of various file types. This application can process images, videos, and documents to reduce their file size while maintaining reasonable quality.

## Features

- Reduce image sizes through compression and resizing
- Compress videos with FFmpeg (if installed)
- Automatic cleanup of temporary files
- Progress tracking for video processing
- Clean separation of concerns through modular architecture

## Project Structure

The application has been organized into a modular structure for better maintainability:

```
file-size-reducer/
├── app.py                  # Main application entry point
├── config.py               # Configuration settings
├── scheduler.py            # Background task scheduler
├── services/               # Core business logic
│   ├── __init__.py
│   ├── processor.py        # File processing logic
│   └── file_manager.py     # File handling operations
├── utils/                  # Helper functions
│   ├── __init__.py
│   ├── file_utils.py       # File utility functions
│   └── cleanup_utils.py    # Cleanup utility functions
├── routes/                 # API endpoints
│   ├── __init__.py
│   └── file_routes.py      # Routes for file operations
└── templates/              # HTML templates
    └── index.html          # Main page template
```

## Requirements

- Python 3.6+
- Flask
- OpenCV (for image processing)
- FFmpeg (optional, for video processing)
- APScheduler (for background tasks)

## Installation

1. Clone the repository
2. Install dependencies with `pip install -r requirements.txt`
3. Run the application with `python app.py`

## Usage

Open your browser and navigate to `http://localhost:8080` to access the application.

## Code Organization

- **app.py**: Main Flask application setup and server startup
- **config.py**: Configuration settings for the application
- **scheduler.py**: Background task scheduler for file cleanup
- **services/**: Core business logic for file processing
- **utils/**: Helper functions and utilities
- **routes/**: API endpoint definitions

All functions include documentation in both English and Turkish. 