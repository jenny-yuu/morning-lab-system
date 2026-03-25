from sqlalchemy.orm import Session
import models

def get_user(db: Session, line_id: str):
    return db.query(models.User).filter(models.User.line_id == line_id).first()

def create_user(db: Session, line_id: str, name: str, phone: str, address_main: str, address_detail: str):
    db_user = models.User(line_id=line_id, name=name, phone=phone, 
                address_main=address_main, address_detail=address_detail, 
                is_member=1, balance=0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def promote_to_member(db: Session, line_id: str, name: str, phone: str, address_main: str, address_detail: str):
    user = get_user(db, line_id)
    if user:
        user.is_member = 1
        user.name = name
        user.phone = phone
        user.address_main = address_main
        user.address_detail = address_detail
    else:
        user = models.User(
            line_id=line_id, 
            name=name, 
            phone=phone, 
            address_main=address_main, 
            address_detail=address_detail,
            is_member=1,
            balance=0
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_balance(db: Session, line_id: str, amount: int, tx_type: str):
    user = get_user(db, line_id)
    if user:
        user.balance += amount
        db.commit()
        # 紀錄交易
        tx = models.Transaction(user_id=line_id, amount=amount, type=tx_type)
        db.add(tx)
        db.commit()
        return user
    return None

def get_daily_order_count(db: Session, date: str):
    return db.query(models.Order).filter(models.Order.delivery_date == date).count()

def create_order(db: Session, user_id: str, items: str, price: int, date: str, address_main: str = None, address_detail: str = None):
    db_order = models.Order(
        user_id=user_id, 
        items=items, 
        total_price=price, 
        delivery_date=date,
        address_main=address_main,
        address_detail=address_detail
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order
