#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import platform
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("build-gui")

def ensure_dependencies():
    """Ensure all required packages are installed."""
    required_packages = [
        "pyinstaller",
        "pillow",
        "google-generativeai",
        "pysubs2"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            logger.info(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def generate_icon():
    """Generate the application icon."""
    # Create assets directory if it doesn't exist
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Add assets directory to Python path temporarily
    sys.path.insert(0, str(assets_dir))
    
    try:
        from generate_icon import create_icon
        icon_path = assets_dir / "icon.ico"
        create_icon(str(icon_path))
        
        # Verify icon was created
        if not icon_path.exists():
            raise FileNotFoundError("Icon file was not created")
        
        # Verify icon size
        if icon_path.stat().st_size < 1000:  # Arbitrary minimum size
            raise ValueError("Generated icon is too small")
            
        logger.info("Icon generated successfully")
    finally:
        # Remove assets directory from Python path
        sys.path.pop(0)

def generate_build_files():
    """Generate build configuration files."""
    # Add assets directory to Python path temporarily
    assets_dir = Path("assets")
    sys.path.insert(0, str(assets_dir))
    
    try:
        from generate_build_files import main as generate_files
        generate_files()
        logger.info("Build configuration files generated successfully")
    finally:
        # Remove assets directory from Python path
        sys.path.pop(0)

def build_executable():
    """Build the executable using PyInstaller."""
    # Clean previous builds
    dist_dir = Path("dist")
    build_dir = Path("build")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Verify required files exist
    required_files = [
        Path("assets/SubSpell.spec"),
        Path("assets/app.manifest"),
        Path("assets/file_version_info.txt"),
        Path("assets/icon.ico")
    ]
    
    for file in required_files:
        if not file.exists():
            raise FileNotFoundError(f"Required file not found: {file}")
    
    # Build the executable
    logger.info("Building executable...")
    subprocess.check_call([
        sys.executable,
        "-m",
        "PyInstaller",
        str(Path("assets/SubSpell.spec"))
    ])
    
    # Verify executable was created
    if platform.system() == "Windows":
        exe_path = dist_dir / "SubSpell.exe"
    else:
        exe_path = dist_dir / "SubSpell"
    
    if not exe_path.exists():
        raise FileNotFoundError("Executable was not created")
    
    # Sign the executable if on Windows and certificate is available
    if platform.system() == "Windows" and os.environ.get("SIGN_CERTIFICATE"):
        try:
            logger.info("Signing executable...")
            subprocess.check_call([
                "signtool",
                "sign",
                "/f", os.environ["SIGN_CERTIFICATE"],
                "/p", os.environ.get("SIGN_PASSWORD", ""),
                "/t", "http://timestamp.digicert.com",
                str(exe_path)
            ])
            logger.info("Executable signed successfully")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to sign executable: {e}")
    
    logger.info(f"Build completed successfully. Executable location: {exe_path}")

def main():
    """Main build process."""
    try:
        logger.info("Starting build process...")
        
        # Ensure dependencies
        ensure_dependencies()
        
        # Generate icon
        generate_icon()
        
        # Generate build files
        generate_build_files()
        
        # Build executable
        build_executable()
        
        logger.info("Build process completed successfully!")
        
    except Exception as e:
        logger.error(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 