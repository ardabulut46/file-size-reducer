#!/usr/bin/env python3
import os
import sys
import subprocess

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible in the PATH."""
    try:
        # Run ffmpeg -version and capture output
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        # Check if the command was successful
        if result.returncode == 0:
            version_line = result.stdout.strip().split('\n')[0]
            print(f"✅ FFmpeg is installed: {version_line}")
            return True
        else:
            print("❌ FFmpeg is installed but returned an error.")
            print(f"Error: {result.stderr}")
            return False
    
    except FileNotFoundError:
        print("❌ FFmpeg is not installed or not in your PATH.")
        print("\nInstallation instructions:")
        
        if sys.platform.startswith('win'):
            print("""
For Windows:
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract the ZIP file
3. Add the bin folder to your system PATH
            """)
        elif sys.platform.startswith('darwin'):
            print("""
For macOS:
1. Install Homebrew if not already installed:
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. Install FFmpeg:
   brew install ffmpeg
            """)
        else:
            print("""
For Ubuntu/Debian:
1. Update package list:
   sudo apt update
2. Install FFmpeg:
   sudo apt install ffmpeg
            """)
        
        return False

def main():
    print("Checking system requirements for File Size Reducer...")
    
    ffmpeg_installed = check_ffmpeg()
    
    if ffmpeg_installed:
        print("\n✅ Your system meets all requirements for File Size Reducer!")
    else:
        print("\n❌ Please install FFmpeg to use all features of File Size Reducer.")
        print("   After installing FFmpeg, run this script again to verify.")
    
    return 0 if ffmpeg_installed else 1

if __name__ == "__main__":
    sys.exit(main()) 