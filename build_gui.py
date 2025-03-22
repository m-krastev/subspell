import os
import sys
import subprocess
import shutil
from pathlib import Path

def ensure_dependencies():
    """Ensure all required dependencies are installed."""
    print("Checking dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "pillow"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])

def generate_icon():
    """Generate the application icon."""
    print("Generating icon...")
    subprocess.check_call([sys.executable, "generate_icon.py"])
    
    # Verify icon was created
    icon_path = os.path.join("assets", "icon.ico")
    if not os.path.exists(icon_path):
        print(f"Error: Icon file not found at {icon_path}")
        sys.exit(1)
    if os.path.getsize(icon_path) == 0:
        print(f"Error: Icon file is empty at {icon_path}")
        sys.exit(1)
    print(f"Verified icon exists at {icon_path}")

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Verify icon exists before building
    icon_path = os.path.join("assets", "icon.ico")
    if not os.path.exists(icon_path):
        print(f"Error: Icon file not found at {icon_path}")
        sys.exit(1)
    
    # Build the executable
    subprocess.check_call([
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--noconsole",
        "--name=SubSpell",
        f"--icon={icon_path}",
        "--hidden-import=google.genai",
        "--hidden-import=pysubs2",
        "src/subspell/__main__.py"
    ])
    
    print("Build complete!")

def main():
    """Main build process."""
    try:
        ensure_dependencies()
        generate_icon()
        build_executable()
    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 