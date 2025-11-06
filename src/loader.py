"""
Point Cloud Loader
Load and preprocess LAS/LAZ files
"""

import numpy as np
import laspy
from pathlib import Path


class PointCloudLoader:
    """Loader for LAS/LAZ point cloud files"""
    
    def __init__(self, max_points=None, downsample_voxel=None):
        """
        Initialize loader
        
        Args:
            max_points: Maximum number of points to load (None = all)
            downsample_voxel: Voxel size for downsampling in meters (None = no downsampling)
        """
        self.max_points = max_points
        self.downsample_voxel = downsample_voxel
    
    def load(self, filepath):
        """
        Load point cloud from LAS/LAZ file
        
        Args:
            filepath: Path to LAS/LAZ file
            
        Returns:
            points: numpy array (N, 3) - XYZ coordinates
            colors: numpy array (N, 3) - RGB colors (0-1 range), or None
            metadata: dict with file information
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        print(f"📂 Loading {filepath.name}...")
        
        # Read LAS file
        las = laspy.read(filepath)
        
        # Extract XYZ coordinates
        points = np.vstack([las.x, las.y, las.z]).T
        
        print(f"   📊 Loaded {len(points):,} points")
        print(f"   📏 Bounds: X[{points[:, 0].min():.1f}, {points[:, 0].max():.1f}]")
        print(f"              Y[{points[:, 1].min():.1f}, {points[:, 1].max():.1f}]")
        print(f"              Z[{points[:, 2].min():.1f}, {points[:, 2].max():.1f}]")
        
        # Extract colors if available
        colors = None
        try:
            if hasattr(las, 'red'):
                # LAS RGB values are typically 16-bit (0-65535)
                r = las.red / 65535.0
                g = las.green / 65535.0
                b = las.blue / 65535.0
                colors = np.vstack([r, g, b]).T
                print(f"   🎨 Colors: Available (RGB)")
        except AttributeError:
            print(f"   🎨 Colors: Not available (will use height colormap)")
        
        # Apply downsampling if requested
        if self.downsample_voxel:
            points, colors = self.voxel_downsample(points, colors, self.downsample_voxel)
            print(f"   🔽 Downsampled to {len(points):,} points (voxel={self.downsample_voxel}m)")
        
        # Limit number of points if requested
        if self.max_points and len(points) > self.max_points:
            # Random sampling
            indices = np.random.choice(len(points), self.max_points, replace=False)
            points = points[indices]
            if colors is not None:
                colors = colors[indices]
            print(f"   ✂️  Sampled to {len(points):,} points (max={self.max_points})")
        
        # Metadata
        metadata = {
            'filename': filepath.name,
            'num_points': len(points),
            'bounds': {
                'x': (points[:, 0].min(), points[:, 0].max()),
                'y': (points[:, 1].min(), points[:, 1].max()),
                'z': (points[:, 2].min(), points[:, 2].max()),
            },
            'has_colors': colors is not None,
            'las_version': f"{las.header.version}",
        }
        
        return points, colors, metadata
    
    @staticmethod
    def voxel_downsample(points, colors, voxel_size):
        """
        Downsample point cloud using voxel grid
        
        Args:
            points: Input points (N, 3)
            colors: Input colors (N, 3) or None
            voxel_size: Voxel size in meters
            
        Returns:
            downsampled_points: (M, 3)
            downsampled_colors: (M, 3) or None
        """
        # Compute voxel indices
        voxel_indices = np.floor(points / voxel_size).astype(np.int32)
        
        # Find unique voxels
        _, unique_indices = np.unique(voxel_indices, axis=0, return_index=True)
        
        # Select one point per voxel (could average instead)
        downsampled_points = points[unique_indices]
        downsampled_colors = colors[unique_indices] if colors is not None else None
        
        return downsampled_points, downsampled_colors
    
    @staticmethod
    def center_points(points):
        """
        Center point cloud at origin
        
        Args:
            points: Input points (N, 3)
            
        Returns:
            centered_points: (N, 3)
            center: (3,) - the original center
        """
        center = points.mean(axis=0)
        centered_points = points - center
        return centered_points, center
    
    @staticmethod
    def normalize_points(points):
        """
        Normalize points to unit cube [-1, 1]
        
        Args:
            points: Input points (N, 3)
            
        Returns:
            normalized_points: (N, 3)
            scale: float - the scale factor
        """
        # Center first
        centered, center = PointCloudLoader.center_points(points)
        
        # Find max extent
        max_extent = np.abs(centered).max()
        
        # Scale to [-1, 1]
        if max_extent > 0:
            normalized = centered / max_extent
        else:
            normalized = centered
        
        return normalized, max_extent
    
    @staticmethod
    def remove_outliers(points, colors=None, nb_neighbors=20, std_ratio=2.0):
        """
        Remove statistical outliers using distance to neighbors
        
        Args:
            points: Input points (N, 3)
            colors: Input colors (N, 3) or None
            nb_neighbors: Number of neighbors to consider
            std_ratio: Standard deviation multiplier
            
        Returns:
            filtered_points: (M, 3) where M <= N
            filtered_colors: (M, 3) or None
        """
        from scipy.spatial import cKDTree
        
        # Build KD-tree
        tree = cKDTree(points)
        
        # Find distances to k nearest neighbors
        distances, _ = tree.query(points, k=nb_neighbors + 1)
        
        # Mean distance for each point (exclude self)
        mean_distances = distances[:, 1:].mean(axis=1)
        
        # Compute threshold
        global_mean = mean_distances.mean()
        global_std = mean_distances.std()
        threshold = global_mean + std_ratio * global_std
        
        # Filter
        mask = mean_distances < threshold
        filtered_points = points[mask]
        filtered_colors = colors[mask] if colors is not None else None
        
        n_removed = len(points) - len(filtered_points)
        print(f"   🧹 Removed {n_removed:,} outliers ({n_removed/len(points)*100:.1f}%)")
        
        return filtered_points, filtered_colors


def load_las_file(filepath, max_points=5000000, downsample=0.05, remove_outliers=False):
    """
    Convenience function to load LAS file with default settings
    
    Args:
        filepath: Path to LAS/LAZ file
        max_points: Maximum points to load
        downsample: Voxel size for downsampling (None to disable)
        remove_outliers: Whether to remove statistical outliers
        
    Returns:
        points: (N, 3) point coordinates
        colors: (N, 3) colors or None
        metadata: dict with file info
    """
    loader = PointCloudLoader(max_points=max_points, downsample_voxel=downsample)
    points, colors, metadata = loader.load(filepath)
    
    if remove_outliers:
        points, colors = PointCloudLoader.remove_outliers(points, colors)
    
    return points, colors, metadata


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python loader.py <path_to_las_file>")
        print("\nExample: python loader.py data/sample.las")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    # Load file
    points, colors, metadata = load_las_file(filepath)
    
    # Print summary
    print("\n📊 Point Cloud Summary:")
    print(f"   Points: {metadata['num_points']:,}")
    print(f"   Has Colors: {metadata['has_colors']}")
    print(f"   LAS Version: {metadata['las_version']}")
    print(f"   X Range: {metadata['bounds']['x'][0]:.2f} to {metadata['bounds']['x'][1]:.2f}")
    print(f"   Y Range: {metadata['bounds']['y'][0]:.2f} to {metadata['bounds']['y'][1]:.2f}")
    print(f"   Z Range: {metadata['bounds']['z'][0]:.2f} to {metadata['bounds']['z'][1]:.2f}")