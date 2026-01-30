from PIL import Image, ImageDraw, ImageFont
import io

def create_window_icon():
    """Crée une icône de fenêtre simple pour RISK-IA"""
    size = 64
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Fond avec dégradé
    for y in range(size):
        r = int(255 * (1 - y/size))
        g = int(107 * (1 - y/size))
        b = int(53 * (1 - y/size))
        draw.line([(0, y), (size, y)], fill=(r, g, b, 100))

    # Cercle central
    center = size // 2
    radius = size // 3
    draw.ellipse([center-radius, center-radius, center+radius, center+radius],
                 fill=(255, 107, 53, 200), outline=(255, 107, 53, 255), width=2)

    # Texte "R-I" simplifié
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    text = "R-I"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    # Convertir en bytes pour PyQt6
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.getvalue()

# Sauvegarder l'icône
if __name__ == "__main__":
    icon_data = create_window_icon()
    with open("window_icon.png", "wb") as f:
        f.write(icon_data)