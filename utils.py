import math

def haversine(lat1, lon1, lat2, lon2):
    """
    計算二點之間的球面距離 (單位：公里)
    """
    # 經緯度轉弧度
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    
    return 2 * 6371 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def is_within_range(user_lat, user_lon, merchant_lat, merchant_lon, max_km=5.0):
    """
    判斷使用者是否在商家的服務範圍內 (預設 5 公里)
    """
    distance = haversine(user_lat, user_lon, merchant_lat, merchant_lon)
    return distance <= max_km, distance
