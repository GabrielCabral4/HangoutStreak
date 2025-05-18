from PIL import Image, ImageDraw
import os

def create_circular_logo(size=512, background_color=(13, 110, 253)):  # Bootstrap primary blue
    # Create a new image with transparency
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Calculate dimensions
    center = size // 2
    main_circle_radius = size * 0.4
    small_circle_radius = size * 0.15
    
    # Draw main circle with gradient
    for r in range(int(main_circle_radius), 0, -1):
        alpha = int(255 * (r / main_circle_radius))
        color = background_color + (alpha,)
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=color
        )
    
    # Calculate positions for small circles
    angles = [0, 120, 240]  # Three circles at 120-degree intervals
    distance = main_circle_radius * 0.8
    
    # Draw connecting circles
    for angle in angles:
        import math
        x = center + distance * math.cos(math.radians(angle))
        y = center + distance * math.sin(math.radians(angle))
        
        # Draw small circle with gradient
        for r in range(int(small_circle_radius), 0, -1):
            alpha = int(255 * (r / small_circle_radius))
            color = background_color + (alpha,)
            draw.ellipse(
                [x - r, y - r, x + r, y + r],
                fill=color
            )
    
    return image

def main():
    # Create directories if they don't exist
    os.makedirs('static/img', exist_ok=True)
    
    # Generate logo
    logo = create_circular_logo()
    
    # Save the logo
    logo_path = 'static/img/logo.png'
    logo.save(logo_path, 'PNG')
    print(f"Logo created successfully at {logo_path}")

if __name__ == '__main__':
    main() 