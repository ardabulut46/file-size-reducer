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

### Image Compression
- Uses OpenCV for high-performance image processing
- Resizes dimensions based on the resize factor
- Reduces quality while maintaining visual appearance
- Optimizes encoding for minimal file size

### Video Compression
- Uses FFmpeg with CRF settings to compress video
- Maintains aspect ratio and frame rate
- Balances quality and file size

### File Storage
- Uploaded files are stored temporarily in the 'uploads' directory
- Processed files are stored in the 'processed' directory
- Files are automatically deleted immediately after download using multiple reliable methods:
  - A background thread that removes files a few seconds after download begins
  - Files are marked for urgent cleanup to be handled by the cleanup scheduler
  - Backup mechanisms to ensure deletion even in case of connection issues
- A background scheduler runs every minute to ensure no files remain on the server
- Regular files are cleaned up after 10 minutes, urgent files after 1 minute
- No persistent storage of user files to maintain privacy and save disk space

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Docker Deployment

This application can be easily deployed using Docker:

### Local Development

```bash
# Build and run with docker-compose
docker-compose up -d
```

### DigitalOcean Deployment

1. Push your code to GitHub
2. Create a new DigitalOcean Droplet with Docker pre-installed
3. SSH into your Droplet
4. Clone your repository
5. Run the application with Docker:

```bash
# Clone the repository
git clone <your-repo-url>
cd <your-repo-directory>

# Build and run the Docker container
docker build -t file-size-reducer .
docker run -d -p 80:8080 -v $(pwd)/uploads:/app/uploads -v $(pwd)/processed:/app/processed --name file-reducer file-size-reducer
```

Alternatively, use DigitalOcean's App Platform with the Dockerfile-based deployment option:

1. Select your repository
2. Choose "Dockerfile" as the deployment method
3. Configure the HTTP port as 8080
4. Deploy the application 