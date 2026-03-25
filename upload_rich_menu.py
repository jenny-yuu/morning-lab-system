import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
SECRET = os.getenv("LINE_CHANNEL_SECRET")

def upload_rich_menu():
    if not ACCESS_TOKEN:
        print("Error: LINE_CHANNEL_ACCESS_TOKEN not found in .env")
        return

    # 1. Create Rich Menu Structure
    with open("rich_menu.json", "r", encoding="utf-8") as f:
        rich_menu_data = json.load(f)

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Delete existing rich menus first (optional, for clean start)
    # requests.delete("https://api.line.me/v2/bot/richmenu/...", ...)

    response = requests.post(
        "https://api.line.me/v2/bot/richmenu",
        headers=headers,
        data=json.dumps(rich_menu_data)
    )

    if response.status_code != 200:
        print(f"Failed to create rich menu: {response.text}")
        return

    rich_menu_id = response.json().get("richMenuId")
    print(f"Successfully created rich menu: {rich_menu_id}")

    # 2. Upload Image
    img_path = "rich_menu_clean.png"
    
    with open(img_path, "rb") as f:
        img_response = requests.post(
            f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content",
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "image/png"
            },
            data=f
        )
    
    if img_response.status_code == 200:
        print("Successfully uploaded rich menu image!")
    else:
        print(f"Failed to upload image: {img_response.text}")
        return

    # 3. Set as Default Rich Menu
    default_response = requests.post(
        f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}",
        headers=headers
    )

    if default_response.status_code == 200:
        print("Successfully set as default rich menu!")
    else:
        print(f"Failed to set default: {default_response.text}")

if __name__ == "__main__":
    upload_rich_menu()
