#!/usr/bin/env python3
"""
Download urban area LAZ files from USGS San Bernardino dataset
These tiles should contain buildings, roads, and city structures
"""

import urllib.request
import sys
from pathlib import Path

# Urban area tiles from San Bernardino city center
# These tiles are more likely to contain buildings and infrastructure
URBAN_TILES = [
    # Downtown/Urban core tiles
    ("https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SanBernardino_EarthMRI_2021_D21/CA_SanBern_EMRI_1_2021/LAZ/USGS_LPC_CA_SanBernardino_EarthMRI_2021_D21_11S_QT_1450.laz", "urban_downtown.laz"),
    ("https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SanBernardino_EarthMRI_2021_D21/CA_SanBern_EMRI_1_2021/LAZ/USGS_LPC_CA_SanBernardino_EarthMRI_2021_D21_11S_QT_1550.laz", "urban_center.laz"),
    ("https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SanBernardino_EarthMRI_2021_D21/CA_SanBern_EMRI_1_2021/LAZ/USGS_LPC_CA_SanBernardino_EarthMRI_2021_D21_11S_QT_1350.laz", "urban_west.laz"),
]

DATA_DIR = Path("../data")

def download_file(url, filepath):
    """Download file with progress indicator"""
    print(f"📥 Downloading: {filepath.name}")
    
    def show_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = downloaded * 100 / total_size
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end='')
    
    try:
        urllib.request.urlretrieve(url, filepath, show_progress)
        file_size = Path(filepath).stat().st_size / (1024 * 1024)
        print(f"\n   ✅ Complete! ({file_size:.1f} MB)")
        return True
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        return False

def main():
    # Create data directory
    DATA_DIR.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("🏙️  Urban Area LiDAR Downloader")
    print("=" * 60)
    print()
    print("Downloading San Bernardino city tiles...")
    print("These should contain buildings and infrastructure")
    print()
    
    downloaded = []
    
    for i, (url, filename) in enumerate(URBAN_TILES, 1):
        filepath = DATA_DIR / filename
        
        # Skip if exists
        if filepath.exists():
            print(f"[{i}/{len(URBAN_TILES)}] ⏭️  Skipping (already exists): {filename}")
            downloaded.append(filepath)
            continue
        
        print(f"[{i}/{len(URBAN_TILES)}] ", end='')
        if download_file(url, filepath):
            downloaded.append(filepath)
        print()
    
    print("=" * 60)
    print(f"✅ Downloaded {len(downloaded)} files")
    print("=" * 60)
    print()
    
    if downloaded:
        print("🎨 View urban areas:")
        for fp in downloaded:
            print(f"  python src/main.py --file {fp}")
        print()
        print("💡 Tip: Try with less downsampling to see buildings:")
        print(f"  python src/main.py --file {downloaded[0]} --downsample 0.02")
        print()

if __name__ == "__main__":
    main()