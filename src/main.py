"""
Main Application
LiDAR Point Cloud Viewer
"""

import argparse
import sys
from pathlib import Path

from renderer import PointCloudRenderer
from loader import load_las_file


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="LiDAR 3D Point Cloud Viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View a LAS file
  python main.py --file data/sample.las
  
  # View with custom settings
  python main.py --file data/sample.las --max-points 1000000 --downsample 0.1
  
  # Smaller window
  python main.py --file data/sample.las --width 1280 --height 720

Controls:
  Left Mouse:  Rotate camera
  Right Mouse: Pan camera
  Mouse Wheel: Zoom
  W/S:         Zoom in/out
  +/-:         Change point size
  R:           Reset camera
  ESC:         Exit
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--file", "-f",
        type=str,
        required=True,
        help="Path to LAS/LAZ file"
    )
    
    # Optional arguments
    parser.add_argument(
        "--max-points",
        type=int,
        default=5000000,
        help="Maximum number of points to load (default: 5M)"
    )
    
    parser.add_argument(
        "--downsample",
        type=float,
        default=0.05,
        help="Voxel size for downsampling in meters (default: 0.05)"
    )
    
    parser.add_argument(
        "--no-downsample",
        action="store_true",
        help="Disable downsampling"
    )
    
    parser.add_argument(
        "--remove-outliers",
        action="store_true",
        help="Remove statistical outliers"
    )
    
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Window width (default: 1920)"
    )
    
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Window height (default: 1080)"
    )
    
    parser.add_argument(
        "--point-size",
        type=float,
        default=2.0,
        help="Initial point size (default: 2.0)"
    )
    
    args = parser.parse_args()
    
    # Check file exists
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"❌ Error: File not found: {filepath}")
        sys.exit(1)
    
    if not filepath.suffix.lower() in ['.las', '.laz']:
        print(f"⚠️  Warning: File extension is {filepath.suffix}, expected .las or .laz")
    
    print("=" * 60)
    print("🚀 LiDAR 3D Point Cloud Viewer")
    print("=" * 60)
    
    # Load point cloud
    try:
        downsample = None if args.no_downsample else args.downsample
        
        points, colors, metadata = load_las_file(
            filepath,
            max_points=args.max_points,
            downsample=downsample,
            remove_outliers=args.remove_outliers
        )
        
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # Create renderer
    try:
        renderer = PointCloudRenderer(
            width=args.width,
            height=args.height,
            title=f"LiDAR Viewer - {filepath.name}"
        )
        
        renderer.point_size = args.point_size
        
    except Exception as e:
        print(f"❌ Error creating renderer: {e}")
        print("\n💡 Tips:")
        print("   - Make sure you have OpenGL support")
        print("   - Update your graphics drivers")
        print("   - Try running with: LIBGL_ALWAYS_SOFTWARE=1 python main.py ...")
        sys.exit(1)
    
    # Load points into renderer
    renderer.load_points(points, colors)
    
    print("=" * 60)
    
    # Run viewer
    try:
        renderer.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during rendering: {e}")
        sys.exit(1)
    
    print("\n✅ Done!")


def quick_test():
    """Quick test with synthetic data"""
    import numpy as np
    
    print("=" * 60)
    print("🧪 Running Quick Test (Synthetic Data)")
    print("=" * 60)
    
    # Generate synthetic point cloud
    print("\nGenerating synthetic point cloud...")
    n_points = 100000
    
    # Create a sphere
    theta = np.random.uniform(0, 2 * np.pi, n_points)
    phi = np.random.uniform(0, np.pi, n_points)
    r = np.random.uniform(0, 10, n_points)
    
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    
    points = np.column_stack([x, y, z])
    
    print(f"   Generated {len(points):,} points")
    
    # Create renderer
    renderer = PointCloudRenderer(
        width=1280,
        height=720,
        title="LiDAR Viewer - Test (Synthetic Sphere)"
    )
    
    # Load points
    renderer.load_points(points)
    
    print("=" * 60)
    
    # Run
    renderer.run()
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    # If no arguments provided, run test
    if len(sys.argv) == 1:
        print("No arguments provided. Running test mode...\n")
        quick_test()
    else:
        main()