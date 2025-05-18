from PIL import Image
import os

def generate_pwa_icons(source_logo='static/img/logo.png'):
    # PWA icon sizes required
    sizes = [
        72, 96, 128, 144, 152, 192, 384, 512
    ]
    
    # Create icons directory if it doesn't exist
    icons_dir = 'static/pwa/icons'
    os.makedirs(icons_dir, exist_ok=True)
    
    # Open source logo
    try:
        logo = Image.open(source_logo)
    except FileNotFoundError:
        print(f"Error: Source logo not found at {source_logo}")
        return
    
    # Generate icons for each size
    for size in sizes:
        # Resize the logo
        icon = logo.resize((size, size), Image.Resampling.LANCZOS)
        
        # Save the icon
        icon_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        icon.save(icon_path, 'PNG')
        print(f"Generated icon: {icon_path}")

if __name__ == '__main__':
    generate_pwa_icons() 