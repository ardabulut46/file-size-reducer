# File Size Reducer

A powerful and easy-to-use web application for reducing the size of various file types including images (JPG, PNG, GIF), videos (MP4, AVI, MOV), and documents.

## Features

- **Multi-file type support**: Reduces the size of images, videos, and documents
- **Large file handling**: Can process files up to 10GB
- **Drag & Drop interface**: Easy-to-use modern web interface
- **Customizable compression**: Adjust quality and size settings for optimal results
- **Progress tracking**: Real-time progress indicators for uploads and processing
- **Comparison visualization**: See before and after file sizes with visual comparison
- **Automatic file cleanup**: Files are automatically deleted after download or after 15 minutes

## Requirements

- Python 3.6 or higher
- FFmpeg installed on your system (for video compression)

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/ardabulut46/file-size-reducer.git
cd file-size-reducer
```

2. **Install the Python dependencies**

```bash
pip install -r requirements.txt
```

3. **Install FFmpeg** (if not already installed)

For Windows:
- Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Add FFmpeg to your system PATH

For macOS:
```bash
brew install ffmpeg
```

For Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

## Usage

1. **Start the application**

```bash
python app.py
```

2. **Access the web interface**

Open your browser and navigate to [http://localhost:5000](http://localhost:5000)

3. **Reduce file size**

- Drag and drop a file into the upload area or click "Select File"
- Adjust compression options based on the file type
- Click "Compress File" to start the process
- Download the reduced file when processing is complete

## Compression Options

### Images
- **Quality**: Adjust the quality percentage (lower values = smaller files)
- **Resize Factor**: Scale the image dimensions (smaller values = smaller files)

### Videos
- **CRF (Constant Rate Factor)**: Controls the quality/size balance (higher values = smaller files)

## How It Works

### Application Architecture
- Flask-based web application with a responsive front-end
- RESTful API endpoints handle file uploads, processing, and downloads
- Asynchronous processing for better user experience
- Real-time progress updates using WebSockets

### Image Compression
- Uses OpenCV for high-performance image processing
- Applies intelligent resizing based on user-defined parameters
- Employs quality reduction algorithms that maintain visual fidelity
- Optimizes metadata and color spaces for minimal file size
- Supports format conversion for optimal compression

### Video Compression
- Leverages FFmpeg with customized encoding parameters
- Uses advanced CRF (Constant Rate Factor) settings for optimal quality/size ratio
- Maintains aspect ratio, frame rate, and audio quality
- Implements multi-pass encoding for complex videos when needed
- Preserves important metadata while stripping unnecessary information

### Document Compression
- Implements PDF optimization techniques
- Reduces embedded image quality
- Removes redundant information and unnecessary metadata

### File Storage & Security
- Uploaded files are stored temporarily in the 'uploads' directory
- Processed files are stored in the 'processed' directory
- Robust file cleanup system:
  - Files are deleted immediately after download via multiple mechanisms
  - Background cleanup scheduler runs periodically
  - Regular files are removed after 10 minutes, urgent files after 1 minute
- Zero persistent storage of user files ensures privacy and security
- Unique file identifiers prevent collision and unauthorized access

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Docker Deployment

You can run this application using Docker without downloading the repository:

```bash
# Pull and run directly from Docker Hub
docker run -d -p 5000:5000 --name file-reducer ardabulut46/file-size-reducer:latest
```

### Custom Configuration with Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3'
services:
  file-reducer:
    image: ardabulut46/file-size-reducer:latest
    ports:
      - "5000:5000"
    volumes:
      - ./data/uploads:/app/uploads
      - ./data/processed:/app/processed
    restart: unless-stopped
```

Then run:

```bash
docker-compose up -d
```

Access the application at [http://localhost:5000](http://localhost:5000) 