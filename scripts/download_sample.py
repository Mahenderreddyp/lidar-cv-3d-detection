#!/usr/bin/env python3
"""
Download sample LAZ file from USGS
San Bernardino, California LiDAR data
"""

import urllib.request
import sys
from pathlib import Path

# Pick a small-ish file to download (they're usually 10-50 MB each)
SAMPLE_URL = "https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SanBernardino_EarthMRI_2021_D21/CA_SanBern_EMRI_1_2021/LAZ/USGS_LPC_CA_SanBernardino_EarthMRI_2021_D21_11S_QT_1761.laz"

FILENAME = "sample_san_bernardino.laz"
DATA_DIR = Path("../data")

def download_file(url, filepath):
    """Download file with progress indicator"""
    print(f"📥 Downloading: {url.split('/')[-1]}")
    print(f"📁 Saving to: {filepath}")
    print()
    
    def show_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = downloaded * 100 / total_size
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end='')
    
    try:
        filepath, headers = urllib.request.urlretrieve(url, filepath, show_progress)
        print("\n\n✅ Download complete!")
        
        # Get file size
        file_size = Path(filepath).stat().st_size / (1024 * 1024)
        print(f"   File size: {file_size:.1f} MB")
        print(f"   Location: {filepath}")
        
    except Exception as e:
        print(f"\n\n❌ Error downloading file: {e}")
        sys.exit(1)

def main():
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
    
    filepath = DATA_DIR / FILENAME
    
    # Check if file already exists
    if filepath.exists():
        print(f"⚠️  File already exists: {filepath}")
        response = input("Download again? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    print("=" * 60)
    print("📡 USGS LiDAR Data Downloader")
    print("=" * 60)
    print()
    print("Dataset: San Bernardino, California")
    print("Source: USGS Earth Explorer")
    print("Format: LAZ (compressed LAS)")
    print()
    
    # Download
    download_file(SAMPLE_URL, filepath)
    
    print()
    print("=" * 60)
    print("🎉 Ready to visualize!")
    print("=" * 60)
    print()
    print("Run the viewer:")
    print(f"  python main.py --file {filepath}")
    print()
    print("Or with downsampling for better performance:")
    print(f"  python main.py --file {filepath} --downsample 0.1")
    print()

if __name__ == "__main__":
    main()