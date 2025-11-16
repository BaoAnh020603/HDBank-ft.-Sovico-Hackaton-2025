"""
Mock User Data - Dữ liệu user giả lập đơn giản
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

# Mock user database
MOCK_USERS = {
    "user_001": {
        "user_id": "user_001",
        "full_name": "Nguyễn Văn A",
        "email": "nguyenvana@gmail.com",
        "phone": "0901234567",
        "id_number": "123456789012",
        "loyalty_points": 250,
        "total_bookings": 3,
        "preferred_payment": "momo"
    },
    "user_002": {
        "user_id": "user_002", 
        "full_name": "Trần Thị B",
        "email": "tranthib@gmail.com",
        "phone": "0907654321",
        "id_number": "987654321098",
        "loyalty_points": 150,
        "total_bookings": 2,
        "preferred_payment": "banking"
    },
    "user_003": {
        "user_id": "user_003",
        "full_name": "Lê Minh C", 
        "email": "leminhc@gmail.com",
        "phone": "0912345678",
        "id_number": "456789123456",
        "loyalty_points": 500,
        "total_bookings": 8,
        "preferred_payment": "visa"
    },
    "user_004": {
        "user_id": "user_004",
        "full_name": "Đinh Như Khải",
        "email": "khaidevcontact@gmail.com",
        "phone": "0888888888",
        "id_number": "0123456789123",
        "loyalty_points": 100,
        "total_bookings": 1,
        "preferred_payment": "momo"
    }
}

# Mock booking history
MOCK_BOOKINGS = {
    "booking_001": {
        "booking_id": "booking_001",
        "user_id": "user_001",
        "service_type": "flight",
        "flight_id": "VJ112",
        "booking_reference": "SOVICO20250922ABC123",
        "total_amount": 1665967,
        "status": "completed",
        "created_at": "2025-09-20T10:30:00"
    },
    "booking_002": {
        "booking_id": "booking_002", 
        "user_id": "user_001",
        "service_type": "hotel",
        "hotel_name": "Lotte Hotel Hanoi",
        "booking_reference": "SOVICO20250918DEF456",
        "total_amount": 2500000,
        "status": "completed",
        "created_at": "2025-09-18T14:20:00"
    },
    "booking_003": {
        "booking_id": "booking_003",
        "user_id": "user_004",
        "service_type": "flight",
        "flight_id": "VJ114",
        "booking_reference": "SOVICO20250920GHI789",
        "total_amount": 1721499,
        "status": "completed",
        "created_at": "2025-09-20T16:45:00"
    }
}

def find_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """Tìm user theo số điện thoại"""
    for user in MOCK_USERS.values():
        if user["phone"] == phone:
            return user
    return None

def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Tìm user theo email"""
    for user in MOCK_USERS.values():
        if user["email"] == email:
            return user
    return None

def create_mock_user(user_info: Dict[str, Any]) -> str:
    """Tạo user mock mới"""
    user_id = f"user_{len(MOCK_USERS) + 1:03d}"
    
    MOCK_USERS[user_id] = {
        "user_id": user_id,
        "full_name": user_info.get("full_name", ""),
        "email": user_info.get("email", ""),
        "phone": user_info.get("phone", ""),
        "id_number": user_info.get("id_number", ""),
        "loyalty_points": 0,
        "total_bookings": 0,
        "preferred_payment": "momo"
    }
    
    return user_id

def get_user_bookings(user_id: str) -> List[Dict[str, Any]]:
    """Lấy booking history của user"""
    bookings = []
    for booking in MOCK_BOOKINGS.values():
        if booking["user_id"] == user_id:
            bookings.append(booking)
    return bookings

def add_mock_booking(user_id: str, booking_data: Dict[str, Any]) -> str:
    """Thêm booking mock"""
    booking_id = f"booking_{len(MOCK_BOOKINGS) + 1:03d}"
    
    MOCK_BOOKINGS[booking_id] = {
        "booking_id": booking_id,
        "user_id": user_id,
        "service_type": booking_data.get("service_type", "flight"),
        "booking_reference": booking_data.get("booking_reference", ""),
        "total_amount": booking_data.get("total_amount", 0),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    # Cập nhật user stats
    if user_id in MOCK_USERS:
        MOCK_USERS[user_id]["total_bookings"] += 1
    
    return booking_id

def get_user_stats(user_id: str) -> Dict[str, Any]:
    """Lấy thống kê user"""
    if user_id not in MOCK_USERS:
        return {}
    
    user = MOCK_USERS[user_id]
    bookings = get_user_bookings(user_id)
    
    total_spent = sum(b.get("total_amount", 0) for b in bookings if b.get("status") == "completed")
    
    return {
        "total_bookings": user["total_bookings"],
        "total_spent": total_spent,
        "loyalty_points": user["loyalty_points"],
        "preferred_payment": user["preferred_payment"]
    }