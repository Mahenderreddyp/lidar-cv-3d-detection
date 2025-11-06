# Testing the Renderer

## ✅ Phase 1 Complete: 3D Viewer Working!

You can now visualize point clouds in 3D!

## Quick Test (No LAS file needed)

```bash
# Run with synthetic data
cd src
python main.py
```

This will create a synthetic sphere with 100,000 points and display it in 3D.

## Test with Real LAS File

```bash
# Basic usage
cd src
python main.py --file ../data/sample.las

# With custom settings
python main.py --file ../data/sample.las --max-points 1000000 --downsample 0.1

# Smaller window for testing
python main.py --file ../data/sample.las --width 1280 --height 720
```

## Controls

- **Left Mouse + Drag**: Rotate camera
- **Right Mouse + Drag**: Pan camera
- **Mouse Wheel**: Zoom in/out
- **W/S**: Zoom in/out (keyboard)
- **+/-**: Increase/decrease point size
- **R**: Reset camera
- **ESC**: Exit

## Getting Sample Data

### Option 1: Download Real LiDAR Data

Visit: https://earthexplorer.usgs.gov/
1. Search for your area
2. Select "Lidar Point Cloud"
3. Download LAS file
4. Place in `data/` folder

### Option 2: Generate Test Data

We can create a script to generate synthetic LAS files for testing.

## What Works Now

✅ **Renderer** (`src/renderer.py`)
- OpenGL 3D visualization
- Camera controls (rotate, pan, zoom)
- Height-based coloring
- Coordinate axes
- 60 FPS with millions of points

✅ **Loader** (`src/loader.py`)
- Load LAS/LAZ files
- Voxel downsampling
- Statistical outlier removal
- RGB color extraction
- Memory-efficient loading

✅ **Main App** (`src/main.py`)
- Command-line interface
- Test mode with synthetic data
- Configurable settings
- Error handling

## What's Next

🔄 **Phase 2: Better Preprocessing**
- Ground segmentation (RANSAC)
- Clustering
- Normal estimation

🔄 **Phase 3: Object Detection**
- PointNet++ model
- Multi-class detection
- Bounding boxes
- Export to GeoJSON

## Performance Tips

For best performance:

1. **Use downsampling** for large files (>5M points)
   ```bash
   python main.py --file data/large.las --downsample 0.1
   ```

2. **Limit points** for testing
   ```bash
   python main.py --file data/large.las --max-points 1000000
   ```

3. **Adjust point size** for visibility
   - Press `+` to increase
   - Press `-` to decrease

## Troubleshooting

### "OpenGL initialization failed"

**Solution:** Update graphics drivers
```bash
# Linux: Check OpenGL support
glxinfo | grep OpenGL

# If no GPU, use software rendering
LIBGL_ALWAYS_SOFTWARE=1 python main.py
```

### "Out of memory"

**Solution:** Reduce points
```bash
python main.py --file data/large.las --max-points 500000 --downsample 0.2
```

### "Module not found"

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

## Example Output

```
============================================================
🚀 LiDAR 3D Point Cloud Viewer
============================================================
📂 Loading sample.las...
   📊 Loaded 2,547,314 points
   📏 Bounds: X[320000.0, 321000.0]
              Y[4650000.0, 4651000.0]
              Z[100.0, 150.0]
   🎨 Colors: Not available (will use height colormap)
   🔽 Downsampled to 245,123 points (voxel=0.05m)

✅ Renderer initialized
   Window: 1920x1080
   OpenGL Version: 4.6

✅ Loaded 245,123 points
   Bounds: X[320000.0, 321000.0]
           Y[4650000.0, 4651000.0]
           Z[100.0, 150.0]
============================================================

🎮 Controls:
   Left Mouse: Rotate
   Right Mouse: Pan
   Scroll: Zoom
   W/S: Zoom in/out
   +/-: Change point size
   R: Reset camera
   ESC: Exit
```

## Code Structure

```python
# Simple usage example
from renderer import PointCloudRenderer
from loader import load_las_file

# Load data
points, colors, metadata = load_las_file('data/sample.las')

# Create renderer
renderer = PointCloudRenderer()

# Display
renderer.load_points(points, colors)
renderer.run()
```