from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    line_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True) # 訪客暫時不填名字
    phone = Column(String, nullable=True)
    address_main = Column(String, nullable=True) # 用於距離檢查的地址
    address_detail = Column(String, nullable=True) # 社區/大樓/戶號
    is_member = Column(Integer, default=0) # 0: 訪客, 1: 儲值會員
    balance = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.line_id"))
    amount = Column(Integer)
    type = Column(String) # Topup, Payment
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.line_id"))
    items = Column(String) # 存 JSON 字串
    total_price = Column(Integer)
    delivery_date = Column(String, index=True) 
    address_main = Column(String, nullable=True)
    address_detail = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
