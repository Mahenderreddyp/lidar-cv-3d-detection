#!/usr/bin/env python3
"""
Generate synthetic urban scene with buildings, roads, trees, and cars
Perfect for testing and demonstration
"""

import numpy as np
import laspy
from pathlib import Path

def create_building(center, width, length, height, classification=6):
    """Create a rectangular building with realistic density"""
    if len(center) == 2:
        x, y = center
        z = 0  # Ground level
    else:
        x, y, z = center
    points = []
    
    # Roof (dense)
    density = 0.3
    for xi in np.arange(-width/2, width/2, density):
        for yi in np.arange(-length/2, length/2, density):
            points.append([x + xi, y + yi, z + height])
    
    # Walls (vertical surfaces)
    wall_density = 0.4
    for h in np.arange(0, height, wall_density):
        # Front and back walls
        for xi in np.arange(-width/2, width/2, density):
            points.append([x + xi, y - length/2, z + h])
            points.append([x + xi, y + length/2, z + h])
        # Left and right walls
        for yi in np.arange(-length/2, length/2, density):
            points.append([x - width/2, y + yi, z + h])
            points.append([x + width/2, y + yi, z + h])
    
    points = np.array(points)
    classes = np.full(len(points), classification, dtype=np.uint8)
    return points, classes

def create_ground(bounds, z_level=0, classification=2):
    """Create ground plane with slight variations"""
    x_min, x_max, y_min, y_max = bounds
    density = 0.8
    
    points = []
    for x in np.arange(x_min, x_max, density):
        for y in np.arange(y_min, y_max, density):
            z = z_level + np.random.normal(0, 0.05)
            points.append([x, y, z])
    
    points = np.array(points)
    classes = np.full(len(points), classification, dtype=np.uint8)
    return points, classes

def create_road(center, width, length, orientation='horizontal', classification=11):
    """Create a road"""
    x, y = center
    density = 0.5
    points = []
    
    if orientation == 'horizontal':
        for xi in np.arange(-length/2, length/2, density):
            for yi in np.arange(-width/2, width/2, density):
                points.append([x + xi, y + yi, 0.05])
    else:  # vertical
        for xi in np.arange(-width/2, width/2, density):
            for yi in np.arange(-length/2, length/2, density):
                points.append([x + xi, y + yi, 0.05])
    
    points = np.array(points)
    classes = np.full(len(points), classification, dtype=np.uint8)
    return points, classes

def create_tree(center, height, crown_radius, classification=5):
    """Create a tree with trunk and crown"""
    if len(center) == 2:
        x, y = center
        z = 0  # Ground level
    else:
        x, y, z = center
    points = []
    
    # Crown (spherical)
    crown_height = z + height * 0.7
    n_points = 500
    
    for _ in range(n_points):
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.random.uniform(0, np.pi)
        r = np.random.uniform(0, crown_radius)
        
        px = x + r * np.sin(phi) * np.cos(theta)
        py = y + r * np.sin(phi) * np.sin(theta)
        pz = crown_height + r * np.cos(phi) * 0.5
        points.append([px, py, pz])
    
    # Trunk
    trunk_density = 0.3
    for h in np.arange(z, crown_height, trunk_density):
        for angle in np.linspace(0, 2*np.pi, 8):
            px = x + 0.3 * np.cos(angle)
            py = y + 0.3 * np.sin(angle)
            points.append([px, py, h])
    
    points = np.array(points)
    classes = np.full(len(points), classification, dtype=np.uint8)
    return points, classes

def create_car(center, length=4.5, width=1.8, height=1.5, classification=1):
    """Create a car"""
    if len(center) == 2:
        x, y = center
        z = 0.1  # Slightly above ground
    else:
        x, y, z = center
    points = []
    density = 0.2
    
    # Car body
    for xi in np.arange(-length/2, length/2, density):
        for yi in np.arange(-width/2, width/2, density):
            for zi in np.arange(0, height, density):
                points.append([x + xi, y + yi, z + zi])
    
    points = np.array(points)
    classes = np.full(len(points), classification, dtype=np.uint8)
    return points, classes

def generate_urban_scene():
    """Generate a complete urban scene"""
    print("🏗️  Generating urban scene...")
    print()
    
    all_points = []
    all_classes = []
    
    # Ground (200m x 200m)
    print("   Creating ground...")
    points, classes = create_ground((-100, 100, -100, 100))
    all_points.append(points)
    all_classes.append(classes)
    print(f"      Added {len(points):,} ground points")
    
    # Roads
    print("   Creating roads...")
    # Main street (horizontal)
    points, classes = create_road((0, 0), 12, 180, 'horizontal')
    all_points.append(points)
    all_classes.append(classes)
    
    # Cross streets (vertical)
    for x_pos in [-60, -20, 20, 60]:
        points, classes = create_road((x_pos, 0), 8, 180, 'vertical')
        all_points.append(points)
        all_classes.append(classes)
    print(f"      Added {sum(len(p) for p in all_points[-5:]):,} road points")
    
    # Buildings (city blocks)
    print("   Creating buildings...")
    buildings = [
        # Left block
        ((-70, 40), 25, 20, 25),   # Building 1
        ((-70, 15), 25, 18, 30),   # Building 2
        ((-70, -15), 25, 20, 20),  # Building 3
        ((-70, -40), 25, 18, 28),  # Building 4
        
        # Center-left block
        ((-35, 40), 22, 20, 35),   # Building 5 (tall)
        ((-35, 15), 22, 18, 22),   # Building 6
        ((-35, -15), 22, 20, 18),  # Building 7
        ((-35, -40), 22, 18, 32),  # Building 8
        
        # Center-right block
        ((5, 40), 20, 18, 28),     # Building 9
        ((5, 15), 20, 20, 40),     # Building 10 (tallest)
        ((5, -15), 20, 18, 25),    # Building 11
        ((5, -40), 20, 20, 30),    # Building 12
        
        # Right block
        ((35, 40), 22, 18, 22),    # Building 13
        ((35, 15), 22, 20, 27),    # Building 14
        ((35, -15), 22, 18, 20),   # Building 15
        ((35, -40), 22, 20, 35),   # Building 16 (tall)
        
        # Far right
        ((70, 40), 20, 18, 18),    # Building 17
        ((70, 15), 20, 20, 25),    # Building 18
        ((70, -15), 20, 18, 23),   # Building 19
        ((70, -40), 20, 20, 28),   # Building 20
    ]
    
    for center, width, length, height in buildings:
        points, classes = create_building(center, width, length, height)
        all_points.append(points)
        all_classes.append(classes)
    
    print(f"      Added {len(buildings)} buildings with {sum(len(p) for p in all_points[-len(buildings):]):,} points")
    
    # Trees (parks and sidewalks)
    print("   Creating vegetation...")
    tree_positions = [
        # Park area (top right)
        ((85, 70), 8, 3), ((90, 75), 7, 2.5), ((80, 75), 6, 2.8),
        ((85, 80), 7.5, 3), ((90, 85), 6.5, 2.5),
        
        # Street trees
        ((-50, 8), 6, 2), ((-30, 8), 5.5, 2), ((-10, 8), 6, 2),
        ((10, 8), 5.5, 2), ((30, 8), 6, 2), ((50, 8), 5.5, 2),
        
        ((-50, -8), 6, 2), ((-30, -8), 5.5, 2), ((-10, -8), 6, 2),
        ((10, -8), 5.5, 2), ((30, -8), 6, 2), ((50, -8), 5.5, 2),
    ]
    
    for center, height, radius in tree_positions:
        points, classes = create_tree(center, height, radius)
        all_points.append(points)
        all_classes.append(classes)
    
    print(f"      Added {len(tree_positions)} trees with {sum(len(p) for p in all_points[-len(tree_positions):]):,} points")
    
    # Cars on roads
    print("   Creating vehicles...")
    car_positions = [
        ((-45, 2), 4.5, 1.8), ((-25, 2), 4.5, 1.8), ((15, 2), 4.5, 1.8),
        ((45, 2), 4.5, 1.8), ((-35, -2), 4.5, 1.8), ((5, -2), 4.5, 1.8),
    ]
    
    for center, length, width in car_positions:
        points, classes = create_car(center, length, width)
        all_points.append(points)
        all_classes.append(classes)
    
    print(f"      Added {len(car_positions)} vehicles with {sum(len(p) for p in all_points[-len(car_positions):]):,} points")
    
    # Combine all points
    all_points = np.vstack(all_points)
    all_classes = np.concatenate(all_classes)
    
    print()
    print(f"✅ Generated {len(all_points):,} total points")
    
    return all_points, all_classes

def save_to_las(points, classes, output_path):
    """Save point cloud to LAS file"""
    print(f"\n💾 Saving to {output_path}...")
    
    # Create LAS header
    header = laspy.LasHeader(version="1.4", point_format=6)
    header.scales = [0.001, 0.001, 0.001]
    header.offsets = [0, 0, 0]
    
    # Create LAS file
    las = laspy.LasData(header)
    
    # Set coordinates
    las.x = points[:, 0]
    las.y = points[:, 1]
    las.z = points[:, 2]
    
    # Set classification
    las.classification = classes
    
    # Write file
    las.write(output_path)
    
    file_size = Path(output_path).stat().st_size / (1024 * 1024)
    print(f"✅ Saved! ({file_size:.2f} MB)")

def main():
    output_dir = Path("../data")
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "synthetic_city.las"
    
    print("=" * 60)
    print("🏙️  Synthetic Urban Scene Generator")
    print("=" * 60)
    print()
    print("Generating realistic city with:")
    print("  • 20 buildings (various heights)")
    print("  • Street grid with roads")
    print("  • Trees and vegetation")
    print("  • Parked vehicles")
    print("  • Ground terrain")
    print()
    
    # Generate scene
    points, classes = generate_urban_scene()
    
    # Save to file
    save_to_las(points, classes, output_path)
    
    print()
    print("=" * 60)
    print("🎉 Ready to visualize!")
    print("=" * 60)
    print()
    print("View the city:")
    print(f"  python src/cityscape_viewer.py --file {output_path}")
    print()
    print("Or with main viewer:")
    print(f"  python src/main.py --file {output_path} --no-downsample")
    print()
    print("🎨 Color Legend:")
    print("  🔴 Red:       Buildings")
    print("  🟤 Brown:     Ground")
    print("  🟢 Green:     Trees")
    print("  ⚫ Dark Gray: Roads")
    print()

if __name__ == "__main__":
    main()