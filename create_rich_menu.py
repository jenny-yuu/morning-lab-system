from PIL import Image, ImageDraw, ImageFont
import os

def create_rich_menu():
    width, height = 2500, 1686
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # Colors
    c1 = (255, 210, 0)   # #FFD200
    c2 = (255, 244, 178) # #FFF4B2
    c3 = (255, 142, 83)  # #FF8E53

    # Draw Panels
    draw.rectangle([0, 0, 833, height], fill=c1)
    draw.rectangle([834, 0, 1667, height], fill=c2)
    draw.rectangle([1668, 0, width, height], fill=c3)

    # Try to load a font (adjust path if needed for Windows)
    try:
        # Windows common fonts
        font_path = "C:\\Windows\\Fonts\\msjhbd.ttc" # Microsoft JhengHei Bold
        if not os.path.exists(font_path):
            font_path = "C:\\Windows\\Fonts\\arial.ttf"
        
        font_main = ImageFont.truetype(font_path, 120)
        font_sub = ImageFont.truetype(font_path, 60)
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Text & Positions
    items = [
        {"txt": "🍳 點餐預約", "desc": "Order Now", "pos": 416, "color": (50, 50, 50)},
        {"txt": "👤 會員中心", "desc": "Member Card", "pos": 1250, "color": (50, 50, 50)},
        {"txt": "💰 儲值專區", "desc": "Top-up Info", "pos": 2084, "color": (255, 255, 255)}
    ]

    for item in items:
        # Main Text
        tw = draw.textlength(item["txt"], font=font_main)
        draw.text((item["pos"] - tw/2, height/2 - 80), item["txt"], fill=item["color"], font=font_main)
        
        # Sub Text
        stw = draw.textlength(item["desc"], font=font_sub)
        draw.text((item["pos"] - stw/2, height/2 + 60), item["desc"], fill=item["color"], font=font_sub)

    # Bottom bar accent
    draw.rectangle([0, height-20, width, height], fill=(50, 50, 50))

    img.save("rich_menu_clean.png")
    print("Successfully created rich_menu_clean.png!")

if __name__ == "__main__":
    create_rich_menu()
