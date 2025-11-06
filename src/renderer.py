"""
OpenGL Point Cloud Renderer
Simple 3D viewer for LiDAR point clouds
"""

import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import glm


class Camera:
    """Simple camera controller for 3D navigation"""
    
    def __init__(self, position=None, target=None):
        self.position = position or glm.vec3(0, 0, 50)
        self.target = target or glm.vec3(0, 0, 0)
        self.up = glm.vec3(0, 0, 1)  # Z-up for GIS data
        
        # Camera parameters
        self.distance = glm.length(self.position - self.target)
        self.azimuth = 45.0  # degrees
        self.elevation = 30.0  # degrees
        
        # Movement speeds
        self.rotation_speed = 0.5
        self.zoom_speed = 2.0
        self.pan_speed = 0.1
        
        self.update_position()
    
    def update_position(self):
        """Update camera position based on spherical coordinates"""
        # Convert to radians
        az_rad = np.radians(self.azimuth)
        el_rad = np.radians(self.elevation)
        
        # Spherical to Cartesian
        x = self.distance * np.cos(el_rad) * np.cos(az_rad)
        y = self.distance * np.cos(el_rad) * np.sin(az_rad)
        z = self.distance * np.sin(el_rad)
        
        self.position = self.target + glm.vec3(x, y, z)
    
    def rotate(self, delta_azimuth, delta_elevation):
        """Rotate camera around target"""
        self.azimuth += delta_azimuth * self.rotation_speed
        self.elevation += delta_elevation * self.rotation_speed
        
        # Clamp elevation to avoid gimbal lock
        self.elevation = np.clip(self.elevation, -89, 89)
        
        self.update_position()
    
    def zoom(self, delta):
        """Zoom in/out"""
        self.distance *= (1.0 - delta * self.zoom_speed * 0.1)
        self.distance = max(1.0, min(self.distance, 1000.0))
        self.update_position()
    
    def pan(self, delta_x, delta_y):
        """Pan camera (move target)"""
        # Get camera right and up vectors
        forward = glm.normalize(self.target - self.position)
        right = glm.normalize(glm.cross(forward, self.up))
        up = glm.cross(right, forward)
        
        # Move target
        move = right * delta_x * self.pan_speed * self.distance * 0.01
        move += up * delta_y * self.pan_speed * self.distance * 0.01
        
        self.target += move
        self.update_position()
    
    def get_view_matrix(self):
        """Get OpenGL view matrix"""
        return glm.lookAt(self.position, self.target, self.up)


class PointCloudRenderer:
    """OpenGL-based point cloud renderer"""
    
    def __init__(self, width=1920, height=1080, title="LiDAR Point Cloud Viewer"):
        self.width = width
        self.height = height
        self.title = title
        
        # Initialize GLFW
        if not glfw.init():
            raise Exception("GLFW initialization failed")
        
        # Create window
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("Window creation failed")
        
        glfw.make_context_current(self.window)
        
        # Camera
        self.camera = Camera()
        
        # Mouse state
        self.mouse_pressed = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_button = None
        
        # Point cloud data
        self.points = None
        self.colors = None
        self.point_size = 2.0
        
        # Setup callbacks
        self.setup_callbacks()
        
        # OpenGL settings
        self.setup_opengl()
        
        print("✅ Renderer initialized")
        print(f"   Window: {width}x{height}")
        print(f"   OpenGL Version: {glGetString(GL_VERSION).decode()}")
    
    def setup_opengl(self):
        """Configure OpenGL settings"""
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Enable point smoothing (anti-aliasing)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        
        # Set point size
        glPointSize(self.point_size)
        
        # Background color (dark gray)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def setup_callbacks(self):
        """Setup mouse and keyboard callbacks"""
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self.mouse_move_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_framebuffer_size_callback(self.window, self.resize_callback)
    
    def mouse_button_callback(self, window, button, action, mods):
        """Handle mouse button events"""
        if action == glfw.PRESS:
            self.mouse_pressed = True
            self.mouse_button = button
            self.last_mouse_x, self.last_mouse_y = glfw.get_cursor_pos(window)
        elif action == glfw.RELEASE:
            self.mouse_pressed = False
            self.mouse_button = None
    
    def mouse_move_callback(self, window, xpos, ypos):
        """Handle mouse movement"""
        if self.mouse_pressed:
            dx = xpos - self.last_mouse_x
            dy = ypos - self.last_mouse_y
            
            if self.mouse_button == glfw.MOUSE_BUTTON_LEFT:
                # Rotate
                self.camera.rotate(dx, -dy)
            elif self.mouse_button == glfw.MOUSE_BUTTON_RIGHT:
                # Pan
                self.camera.pan(-dx, dy)
            
            self.last_mouse_x = xpos
            self.last_mouse_y = ypos
    
    def scroll_callback(self, window, xoffset, yoffset):
        """Handle mouse scroll (zoom)"""
        self.camera.zoom(-yoffset)
    
    def key_callback(self, window, key, scancode, action, mods):
        """Handle keyboard input"""
        if action == glfw.PRESS or action == glfw.REPEAT:
            # ESC to close
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)
            
            # W/S - move forward/back
            elif key == glfw.KEY_W:
                self.camera.zoom(1)
            elif key == glfw.KEY_S:
                self.camera.zoom(-1)
            
            # +/- for point size
            elif key == glfw.KEY_EQUAL or key == glfw.KEY_KP_ADD:
                self.point_size = min(self.point_size + 0.5, 10.0)
                glPointSize(self.point_size)
                print(f"Point size: {self.point_size}")
            elif key == glfw.KEY_MINUS or key == glfw.KEY_KP_SUBTRACT:
                self.point_size = max(self.point_size - 0.5, 1.0)
                glPointSize(self.point_size)
                print(f"Point size: {self.point_size}")
            
            # R - reset camera
            elif key == glfw.KEY_R:
                self.camera = Camera()
                print("Camera reset")
    
    def resize_callback(self, window, width, height):
        """Handle window resize"""
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
    
    def load_points(self, points, colors=None):
        """
        Load point cloud data
        
        Args:
            points: numpy array of shape (N, 3) - XYZ coordinates
            colors: numpy array of shape (N, 3) - RGB colors (0-1 range)
                   If None, colors will be generated from height
        """
        self.points = points.astype(np.float32)
        
        if colors is None:
            # Color by height (Z coordinate)
            colors = self.height_colormap(points[:, 2])
        
        self.colors = colors.astype(np.float32)
        
        # Center camera on point cloud
        center = points.mean(axis=0)
        self.camera.target = glm.vec3(center[0], center[1], center[2])
        
        # Set camera distance based on point cloud size
        bbox_size = points.max(axis=0) - points.min(axis=0)
        max_dim = np.max(bbox_size)
        self.camera.distance = max_dim * 1.5
        self.camera.update_position()
        
        print(f"✅ Loaded {len(points):,} points")
        print(f"   Bounds: X[{points[:, 0].min():.1f}, {points[:, 0].max():.1f}]")
        print(f"           Y[{points[:, 1].min():.1f}, {points[:, 1].max():.1f}]")
        print(f"           Z[{points[:, 2].min():.1f}, {points[:, 2].max():.1f}]")
    
    @staticmethod
    def height_colormap(heights):
        """Generate colors from height using a colormap"""
        # Normalize heights to 0-1
        h_min, h_max = heights.min(), heights.max()
        if h_max > h_min:
            normalized = (heights - h_min) / (h_max - h_min)
        else:
            normalized = np.zeros_like(heights)
        
        # Apply viridis-like colormap (blue -> green -> yellow)
        colors = np.zeros((len(heights), 3), dtype=np.float32)
        
        # Blue to cyan to green to yellow to red
        colors[:, 0] = np.clip(1.5 * normalized - 0.5, 0, 1)  # Red
        colors[:, 1] = np.clip(-2 * np.abs(normalized - 0.5) + 1, 0, 1)  # Green
        colors[:, 2] = np.clip(1.5 * (1 - normalized) - 0.5, 0, 1)  # Blue
        
        return colors
    
    def setup_projection(self):
        """Setup perspective projection"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.width / self.height
        gluPerspective(45, aspect, 0.1, 10000.0)
    
    def setup_modelview(self):
        """Setup model-view matrix"""
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Apply camera view
        view = self.camera.get_view_matrix()
        # Convert GLM matrix to numpy array for OpenGL compatibility
        view_array = np.array(view).T.flatten().astype(np.float32)
        glMultMatrixf(view_array)
    
    def render_points(self):
        """Render point cloud"""
        if self.points is None or self.colors is None:
            return
        
        # Draw points
        glBegin(GL_POINTS)
        for point, color in zip(self.points, self.colors):
            glColor3f(color[0], color[1], color[2])
            glVertex3f(point[0], point[1], point[2])
        glEnd()
    
    def render_axes(self, size=5.0):
        """Render coordinate axes for reference"""
        glLineWidth(2.0)
        glBegin(GL_LINES)
        
        # X axis (red)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(size, 0, 0)
        
        # Y axis (green)
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, size, 0)
        
        # Z axis (blue)
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, size)
        
        glEnd()
        glLineWidth(1.0)
    
    def render_text(self):
        """Render UI text (instructions)"""
        # Note: For simplicity, we skip text rendering
        # In production, you'd use imgui or similar
        pass
    
    def render(self):
        """Main render loop"""
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Setup matrices
        self.setup_projection()
        self.setup_modelview()
        
        # Render content
        self.render_axes()
        self.render_points()
        
        # Swap buffers
        glfw.swap_buffers(self.window)
    
    def run(self):
        """Main application loop"""
        print("\n🎮 Controls:")
        print("   Left Mouse: Rotate")
        print("   Right Mouse: Pan")
        print("   Scroll: Zoom")
        print("   W/S: Zoom in/out")
        print("   +/-: Change point size")
        print("   R: Reset camera")
        print("   ESC: Exit\n")
        
        # Main loop
        while not glfw.window_should_close(self.window):
            # Process events
            glfw.poll_events()
            
            # Render
            self.render()
        
        # Cleanup
        glfw.terminate()
        print("👋 Renderer closed")
    
    def close(self):
        """Close the renderer"""
        glfw.set_window_should_close(self.window, True)


# Example usage
if __name__ == "__main__":
    # Create renderer
    renderer = PointCloudRenderer(width=1280, height=720)
    
    # Generate sample point cloud (random sphere)
    print("Generating sample point cloud...")
    n_points = 100000
    
    # Random points in a sphere
    theta = np.random.uniform(0, 2 * np.pi, n_points)
    phi = np.random.uniform(0, np.pi, n_points)
    r = np.random.uniform(0, 10, n_points)
    
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    
    points = np.column_stack([x, y, z])
    
    # Load points
    renderer.load_points(points)
    
    # Run
    renderer.run()