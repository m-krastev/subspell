#!/usr/bin/env python3
from PIL import Image, ImageDraw
import math

def create_rounded_rectangle(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    
    # Draw the main rectangle
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    
    # Draw the rounded corners
    draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)  # Top left
    draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)  # Top right
    draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)  # Bottom left
    draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)  # Bottom right

def create_icon(output_path, size=256):
    """Create the application icon with a white triangle on black background."""
    # Create a new image with transparency
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Calculate the background rectangle with rounded corners
    margin = size * 0.15
    background_radius = size * 0.25  # Larger radius for the background
    
    # Draw the rounded rectangle background
    create_rounded_rectangle(
        draw,
        [margin, margin, size - margin, size - margin],
        background_radius,
        (0, 0, 0, 255)  # Black background
    )
    
    # Calculate the triangle points
    # Using a slightly smaller size to ensure the triangle fits nicely
    triangle_margin = size * 0.25  # Larger margin for the triangle
    triangle_size = size - 2 * triangle_margin
    
    # Calculate the points for the triangle
    points = [
        (size/2, triangle_margin),  # Top point
        (size - triangle_margin, size - triangle_margin),  # Bottom right
        (triangle_margin, size - triangle_margin)  # Bottom left
    ]
    
    # Draw the triangle
    draw.polygon(points, fill=(255, 255, 255, 255))
    
    # Save the icon
    image.save(output_path, format='ICO', sizes=[(256, 256)])

if __name__ == "__main__":
    create_icon("icon.ico") 