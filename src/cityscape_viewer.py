"""
Enhanced viewer for urban/cityscape LiDAR data
Adds classification-based coloring for buildings, ground, vegetation, etc.
"""

import numpy as np
import laspy
from pathlib import Path
from renderer import PointCloudRenderer

# LAS Classification codes (ASPRS standard)
CLASSIFICATION_COLORS = {
    0: (0.5, 0.5, 0.5),    # Never classified - Gray
    1: (0.3, 0.3, 0.3),    # Unclassified - Dark gray
    2: (0.6, 0.4, 0.2),    # Ground - Brown
    3: (0.2, 0.6, 0.2),    # Low vegetation - Light green
    4: (0.1, 0.7, 0.1),    # Medium vegetation - Green
    5: (0.0, 0.8, 0.0),    # High vegetation - Bright green
    6: (0.9, 0.1, 0.1),    # Building - Red
    7: (0.9, 0.9, 0.0),    # Low point (noise) - Yellow
    9: (0.0, 0.5, 0.9),    # Water - Blue
    10: (0.5, 0.0, 0.9),   # Rail - Purple
    11: (0.3, 0.3, 0.3),   # Road surface - Dark gray
    13: (0.8, 0.8, 0.2),   # Wire - Guard - Yellow
    14: (0.9, 0.5, 0.0),   # Wire - Conductor - Orange
    15: (0.7, 0.3, 0.0),   # Transmission tower - Brown/orange
    17: (0.4, 0.4, 0.4),   # Bridge deck - Gray
    18: (0.0, 0.8, 0.8),   # High noise - Cyan
}

def load_urban_las(filepath, max_points=5000000, downsample_voxel=0.02):
    """
    Load LAS file with classification-based coloring for urban scenes
    
    Args:
        filepath: Path to LAS/LAZ file
        max_points: Maximum points to load
        downsample_voxel: Voxel size for downsampling (smaller = more detail)
    
    Returns:
        points, colors, metadata
    """
    filepath = Path(filepath)
    print(f"📂 Loading urban data: {filepath.name}...")
    
    # Read LAS
    las = laspy.read(filepath)
    points = np.vstack([las.x, las.y, las.z]).T
    
    print(f"   📊 Loaded {len(points):,} points")
    print(f"   📏 Bounds: X[{points[:, 0].min():.1f}, {points[:, 0].max():.1f}]")
    print(f"              Y[{points[:, 1].min():.1f}, {points[:, 1].max():.1f}]")
    print(f"              Z[{points[:, 2].min():.1f}, {points[:, 2].max():.1f}]")
    
    # Check for classification data
    colors = None
    if hasattr(las, 'classification'):
        print(f"   🏗️  Classification data found!")
        
        # Count classes
        unique, counts = np.unique(las.classification, return_counts=True)
        print(f"   📋 Classes present:")
        class_names = {
            2: "Ground", 3: "Low Veg", 4: "Med Veg", 5: "High Veg",
            6: "Building", 7: "Noise", 9: "Water", 11: "Road"
        }
        for cls, count in zip(unique, counts):
            name = class_names.get(cls, f"Class {cls}")
            pct = count / len(points) * 100
            print(f"      {name}: {count:,} points ({pct:.1f}%)")
        
        # Create colors from classification
        colors = np.zeros((len(points), 3), dtype=np.float32)
        for i, cls in enumerate(las.classification):
            colors[i] = CLASSIFICATION_COLORS.get(cls, (0.5, 0.5, 0.5))
        
        print(f"   🎨 Using classification-based colors")
    else:
        print(f"   ⚠️  No classification data, using height colors")
    
    # Downsample
    if downsample_voxel:
        from loader import PointCloudLoader
        points, colors = PointCloudLoader.voxel_downsample(points, colors, downsample_voxel)
        print(f"   🔽 Downsampled to {len(points):,} points (voxel={downsample_voxel}m)")
    
    # Limit points
    if max_points and len(points) > max_points:
        indices = np.random.choice(len(points), max_points, replace=False)
        points = points[indices]
        if colors is not None:
            colors = colors[indices]
        print(f"   ✂️  Sampled to {len(points):,} points")
    
    metadata = {
        'filename': filepath.name,
        'num_points': len(points),
        'has_classification': colors is not None,
    }
    
    return points, colors, metadata


def main():
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Urban LiDAR Viewer")
    parser.add_argument("--file", "-f", required=True, help="Path to LAS/LAZ file")
    parser.add_argument("--max-points", type=int, default=5000000, help="Max points")
    parser.add_argument("--downsample", type=float, default=0.02, help="Voxel size (smaller=more detail)")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏙️  Urban LiDAR Viewer")
    print("=" * 60)
    print()
    
    # Load data
    points, colors, metadata = load_urban_las(
        args.file,
        max_points=args.max_points,
        downsample_voxel=args.downsample
    )
    
    print()
    print("=" * 60)
    
    # Create renderer
    renderer = PointCloudRenderer(
        width=args.width,
        height=args.height,
        title=f"Urban Viewer - {metadata['filename']}"
    )
    
    # Load and display
    renderer.load_points(points, colors)
    
    print("=" * 60)
    print()
    print("🎨 Color Legend:")
    print("   🔴 Red:         Buildings")
    print("   🟤 Brown:       Ground")
    print("   🟢 Green:       Vegetation")
    print("   ⚫ Dark Gray:   Roads")
    print("   🔵 Blue:        Water")
    print()
    
    renderer.run()
    print("\n✅ Done!")


if __name__ == "__main__":
    main()