"""
LiDAR Point Cloud Object Detection & 3D Visualization System
Setup configuration for package installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="lidar-cv-3d-detection",
    version="0.1.0",
    author="Mahender Reddy Pokala",
    author_email="your.email@example.com",
    description="A computer vision system for detecting and visualizing objects in 3D LiDAR point cloud data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lidar-cv-3d-detection",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/lidar-cv-3d-detection/issues",
        "Documentation": "https://github.com/yourusername/lidar-cv-3d-detection/docs",
        "Source Code": "https://github.com/yourusername/lidar-cv-3d-detection",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.2.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "cuda": [
            "cupy-cuda11x>=11.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lidar-viewer=main:main",
            "lidar-detect=main:detect_main",
            "lidar-change=main:change_detection_main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.glsl", "*.vert", "*.frag"],
    },
    keywords=[
        "lidar",
        "point-cloud",
        "computer-vision",
        "object-detection",
        "3d-visualization",
        "opengl",
        "deep-learning",
        "pytorch",
        "geospatial",
        "gis",
        "change-detection",
    ],
    zip_safe=False,
)