import os
from fastapi import FastAPI, Request, HTTPException, Depends
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import database, models, crud, utils
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 載入環境變數
load_dotenv()

# 商家座標 (以此做為基準點)
MERCHANT_LAT = 24.808064
MERCHANT_LON = 121.040176
DAILY_CAPACITY = 10 # 每日限額測試，設小一點方便測試

app = FastAPI()

# LINE 設定
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 掛載靜態檔案 (LIFF 前端)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化資料庫
database.Base.metadata.create_all(bind=database.engine)

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/pay")
async def read_pay():
    return FileResponse('static/payment.html')

# 依賴項：獲取資料庫 Session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/test-distance")
async def test_distance(lat: float, lon: float):
    """
    本地測試用：輸入使用者的經緯度，計算與店家的距離
    """
    within_range, distance = utils.is_within_range(lat, lon, MERCHANT_LAT, MERCHANT_LON)
    return {
        "status": "success",
        "distance_km": round(distance, 2),
        "is_within_range": within_range,
        "merchant_location": {"lat": MERCHANT_LAT, "lon": MERCHANT_LON}
    }

import requests

@app.get("/api/geocode")
async def geocode_address(address: str):
    """
    使用免費的 OpenStreetMap Nominatim API 將地址轉為經緯度
    並計算與店家的距離
    """
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
        headers = {'User-Agent': 'MorningLabSystem/1.0'}
        r = requests.get(url, headers=headers)
        data = r.json()
        
        if not data:
            return {"status": "error", "message": "找不到該地址，請輸入更精確的內容"}
            
        user_lat = float(data[0]["lat"])
        user_lon = float(data[0]["lon"])
        
        within_range, dist = utils.is_within_range(user_lat, user_lon, MERCHANT_LAT, MERCHANT_LON, max_km=5.0)
        
        return {
            "status": "success",
            "lat": user_lat,
            "lon": user_lon,
            "distance_km": round(dist, 2),
            "is_within_range": within_range
        }
    except Exception as e:
        return {"status": "error", "message": f"地理編碼發生錯誤: {str(e)}"}

@app.post("/api/payment-simulate")
async def payment_simulate(request: Request):
    data = await request.json()
    order_id = data.get("order_id")
    # 這裡演示 Webhook 處理邏輯
    print(f"💰 收到支付訊號：訂單 {order_id} 已完成付款")
    return {"status": "success", "message": "後端已收到支付確認"}

@app.get("/api/user/{user_id}")
async def get_user_status(user_id: str):
    db = next(get_db())
    user = crud.get_user(db, user_id)
    if not user:
        return {"status": "guest", "is_member": False, "balance": 0}
    return {
        "status": "success",
        "is_member": bool(user.is_member),
        "name": user.name,
        "balance": user.balance,
        "address": user.address,
        "phone": user.phone
    }

@app.post("/api/payment-simulate")
async def payment_simulate(request: Request):
    data = await request.json()
    order_id = data.get("order_id")
    # 這裡可以擴充資料庫更新邏輯，演示 Webhook 回傳處理
    print(f"Payment simulation received for Order {order_id}")
    return {"status": "success", "message": "已收到支付回報"}

@app.post("/api/test-topup")
async def test_topup(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    amount = data.get("amount", 100)
    db = next(get_db())
    crud.update_balance(db, user_id, amount, "Test Topup")
    return {"status": "success", "message": f"成功儲值 ${amount}"}

@app.post("/api/register")
async def register_member(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    name = data.get("name")
    phone = data.get("phone")
    address = data.get("address")
    
    db = next(get_db())
    crud.promote_to_member(db, user_id, name, phone, address)
    return {"status": "success", "message": "會員註冊成功！"}

@app.post("/api/orders")
async def place_order(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    total_price = data.get("total_price")
    items = data.get("items")
    delivery_date = data.get("delivery_date")
    pay_mode = data.get("pay_mode") # 'guest' or 'member'
    address_main = data.get("address_main")
    address_detail = data.get("address_detail")
    
    db = next(get_db())
    
    # 檢查產能
    current_count = crud.get_daily_order_count(db, delivery_date)
    if current_count >= DAILY_CAPACITY:
        return {"status": "error", "message": f"抱歉，{delivery_date} 已額滿"}
    
    # 會員餘額檢查與扣款
    if pay_mode == 'member':
        user = crud.get_user(db, user_id)
        if not user or user.balance < total_price:
            return {"status": "error", "message": "餘額不足，請先到儲值頁面測試加值！"}
        crud.update_balance(db, user_id, -total_price, f"Order: {delivery_date}") # Assuming update_balance is the correct function
        
    # 建立訂單
    new_order = crud.create_order(db, user_id, items, total_price, delivery_date, address_main, address_detail)
    
    return {
        "status": "success", 
        "order_id": new_order.id,
        "message": "預約成功！" + (" (已從餘額扣款)" if pay_mode == "member" else " (請依指示完成付款)")
    }

@app.get("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    user_id = event.source.user_id
    
    # 獲取資料庫 session
    db = next(get_db())

    # 檢查使用者是否存在，不存在則預設為訪客
    user = crud.get_user(db, user_id)
    if not user:
        user = crud.create_user(db, user_id, name="訪客", is_member=0)

    # 機器人邏輯
    if text == "查詢餘額":
        if user.is_member:
            reply_text = f"你好 {user.name} 會員，你的點數餘額為 ${user.balance} 元。"
        else:
            reply_text = "你目前是「一次性訪客」，尚未開通儲值會員。輸入「我要加入會員」即可開通功能！"
    
    elif text == "我要加入會員":
        # 這裡未來會接選單或問券填寫
        crud.promote_to_member(db, user_id, "測試會員", "0912345678", "竹北高鐵路100號")
        reply_text = "恭喜！你已成為「儲值會員」，現在可以進行存錢與點數扣款了。"
        
    elif text == "增加 100":
        if user.is_member:
            crud.update_balance(db, user_id, 100, "Topup")
            reply_text = "成功！已為會員存入 $100 元點數。"
        else:
            reply_text = "抱歉，訪客不支援儲值功能。請先輸入「我要加入會員」喔！"
    
    elif text == "我要點餐測試":
        target_date = "2026-03-26" # 假設點明天的餐
        current_count = crud.get_daily_order_count(db, target_date)
        
        if current_count >= DAILY_CAPACITY:
            reply_text = f"抱歉！{target_date} 的早餐預約已滿 (上限 {DAILY_CAPACITY} 份)，請選擇其他日期。"
        else:
            # 建立訂單
            crud.create_order(db, user_id, "晨光三明治 x1", 60, target_date)
            reply_text = f"預約成功！這是 {target_date} 的第 {current_count + 1} 份訂單。剩餘名額：{DAILY_CAPACITY - (current_count + 1)}"
    
    elif text == "我要點餐" or text == "菜單":
        reply_text = "Morning Lab 點餐系統已上線：\nhttps://morning-lab-system.onrender.com/"
    else:
        reply_text = f"你說了：{text}\n輸入「查詢餘額」可以看錢包，輸入「增加 100」可以測試存錢。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
