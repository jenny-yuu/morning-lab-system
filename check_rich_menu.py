import os
import requests
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def check_status():
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    # 1. Get default rich menu ID
    r_default = requests.get("https://api.line.me/v2/bot/user/all/richmenu", headers=headers)
    print(f"Default Rich Menu ID: {r_default.json()}")
    
    # 2. List all rich menus
    r_list = requests.get("https://api.line.me/v2/bot/richmenu/list", headers=headers)
    print(f"All Rich Menus: {r_list.json()}")

if __name__ == "__main__":
    check_status()
