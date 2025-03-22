from PIL import Image, ImageDraw
import os
import sys

def create_icon():
    # Create assets directory if it doesn't exist
    assets_dir = "assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    # Create a 256x256 image with black background
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    
    # Draw a white triangle
    # Calculate points for an equilateral triangle
    margin = size // 8
    points = [
        (size // 2, margin),  # top
        (margin, size - margin),  # bottom left
        (size - margin, size - margin),  # bottom right
    ]
    
    # Draw the triangle
    draw.polygon(points, fill=(255, 255, 255, 255))
    
    # Save as ICO file
    icon_path = os.path.join(assets_dir, "icon.ico")
    try:
        # Save with explicit format
        image.save(icon_path, format='ICO', sizes=[(256, 256)])
        
        # Verify the file was created
        if not os.path.exists(icon_path):
            print(f"Error: Icon file was not created at {icon_path}")
            sys.exit(1)
            
        # Verify the file size
        file_size = os.path.getsize(icon_path)
        if file_size == 0:
            print(f"Error: Icon file is empty at {icon_path}")
            sys.exit(1)
            
        print(f"Successfully created icon at {icon_path} (size: {file_size} bytes)")
        
    except Exception as e:
        print(f"Error saving icon: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_icon() 