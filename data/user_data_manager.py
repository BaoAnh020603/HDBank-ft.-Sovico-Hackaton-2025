"""
User Data Manager - Quản lý thông tin người dùng
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

class UserDataManager:
    """Quản lý dữ liệu người dùng"""
    
    def __init__(self, data_file: str = None):
        if not data_file:
            data_dir = os.path.join(os.path.dirname(__file__), "generated")
            os.makedirs(data_dir, exist_ok=True)
            data_file = os.path.join(data_dir, "user_data.json")
        
        self.data_file = data_file
        self.users = self._load_users()
    
    def _load_users(self) -> Dict[str, Any]:
        """Load dữ liệu user từ file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Tạo dữ liệu mặc định
        return {
            "users": {},
            "bookings": {},
            "preferences": {}
        }
    
    def _save_users(self):
        """Lưu dữ liệu user vào file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def create_user(self, user_info: Dict[str, Any]) -> str:
        """Tạo user mới"""
        user_id = str(uuid.uuid4())
        
        user_data = {
            "user_id": user_id,
            "full_name": user_info.get("full_name", ""),
            "email": user_info.get("email", ""),
            "phone": user_info.get("phone", ""),
            "id_number": user_info.get("id_number", ""),
            "date_of_birth": user_info.get("date_of_birth", ""),
            "address": user_info.get("address", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "loyalty_points": 0,
            "total_bookings": 0
        }
        
        self.users["users"][user_id] = user_data
        self.users["preferences"][user_id] = {
            "preferred_airlines": ["VietJet Air"],
            "preferred_class": "Economy",
            "preferred_payment": "momo",
            "notification_email": True,
            "notification_sms": True
        }
        
        self._save_users()
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin user"""
        return self.users["users"].get(user_id)
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Cập nhật thông tin user"""
        if user_id not in self.users["users"]:
            return False
        
        user_data = self.users["users"][user_id]
        user_data.update(updates)
        user_data["updated_at"] = datetime.now().isoformat()
        
        self._save_users()
        return True
    
    def find_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Tìm user theo số điện thoại"""
        for user_id, user_data in self.users["users"].items():
            if user_data.get("phone") == phone:
                return user_data
        return None
    
    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Tìm user theo email"""
        for user_id, user_data in self.users["users"].items():
            if user_data.get("email") == email:
                return user_data
        return None
    
    def add_booking(self, user_id: str, booking_data: Dict[str, Any]) -> str:
        """Thêm booking cho user"""
        booking_id = str(uuid.uuid4())
        
        booking_record = {
            "booking_id": booking_id,
            "user_id": user_id,
            "service_type": booking_data.get("service_type"),
            "service_id": booking_data.get("service_id"),
            "booking_reference": booking_data.get("booking_reference"),
            "confirmation_code": booking_data.get("confirmation_code"),
            "total_amount": booking_data.get("total_amount", 0),
            "payment_status": booking_data.get("payment_status", "pending"),
            "booking_status": booking_data.get("booking_status", "pending"),
            "created_at": datetime.now().isoformat(),
            "booking_details": booking_data
        }
        
        self.users["bookings"][booking_id] = booking_record
        
        # Cập nhật thống kê user
        if user_id in self.users["users"]:
            self.users["users"][user_id]["total_bookings"] += 1
            if booking_data.get("payment_status") == "completed":
                points = int(booking_data.get("total_amount", 0) / 10000)  # 1 điểm/10k VNĐ
                self.users["users"][user_id]["loyalty_points"] += points
        
        self._save_users()
        return booking_id
    
    def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        """Lấy danh sách booking của user"""
        bookings = []
        for booking_id, booking_data in self.users["bookings"].items():
            if booking_data["user_id"] == user_id:
                bookings.append(booking_data)
        
        # Sắp xếp theo thời gian tạo (mới nhất trước)
        return sorted(bookings, key=lambda x: x["created_at"], reverse=True)
    
    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin booking"""
        return self.users["bookings"].get(booking_id)
    
    def update_booking_status(self, booking_id: str, status: str, payment_status: str = None) -> bool:
        """Cập nhật trạng thái booking"""
        if booking_id not in self.users["bookings"]:
            return False
        
        booking = self.users["bookings"][booking_id]
        booking["booking_status"] = status
        
        if payment_status:
            booking["payment_status"] = payment_status
        
        booking["updated_at"] = datetime.now().isoformat()
        
        self._save_users()
        return True
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Lấy preferences của user"""
        return self.users["preferences"].get(user_id, {})
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Cập nhật preferences của user"""
        if user_id not in self.users["users"]:
            return False
        
        if user_id not in self.users["preferences"]:
            self.users["preferences"][user_id] = {}
        
        self.users["preferences"][user_id].update(preferences)
        self._save_users()
        return True
    
    def get_frequent_travelers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Lấy danh sách khách hàng thường xuyên"""
        users = list(self.users["users"].values())
        sorted_users = sorted(users, key=lambda x: x.get("total_bookings", 0), reverse=True)
        return sorted_users[:limit]
    
    def search_users(self, query: str) -> List[Dict[str, Any]]:
        """Tìm kiếm user theo tên, email, phone"""
        results = []
        query_lower = query.lower()
        
        for user_data in self.users["users"].values():
            if (query_lower in user_data.get("full_name", "").lower() or
                query_lower in user_data.get("email", "").lower() or
                query_lower in user_data.get("phone", "")):
                results.append(user_data)
        
        return results
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Lấy thống kê của user"""
        user = self.get_user(user_id)
        if not user:
            return {}
        
        bookings = self.get_user_bookings(user_id)
        
        # Thống kê theo service type
        flight_bookings = [b for b in bookings if b.get("service_type") == "flight"]
        hotel_bookings = [b for b in bookings if b.get("service_type") == "hotel"]
        
        # Tổng chi tiêu
        total_spent = sum(b.get("total_amount", 0) for b in bookings if b.get("payment_status") == "completed")
        
        return {
            "total_bookings": len(bookings),
            "flight_bookings": len(flight_bookings),
            "hotel_bookings": len(hotel_bookings),
            "total_spent": total_spent,
            "loyalty_points": user.get("loyalty_points", 0),
            "member_since": user.get("created_at"),
            "last_booking": bookings[0].get("created_at") if bookings else None
        }

# Global instance
user_data_manager = UserDataManager()

# Helper functions
def create_user_profile(user_info: Dict) -> str:
    """Tạo profile user mới"""
    return user_data_manager.create_user(user_info)

def get_user_profile(user_id: str) -> Optional[Dict]:
    """Lấy profile user"""
    return user_data_manager.get_user(user_id)

def find_user_by_contact(phone: str = None, email: str = None) -> Optional[Dict]:
    """Tìm user theo thông tin liên hệ"""
    if phone:
        return user_data_manager.find_user_by_phone(phone)
    elif email:
        return user_data_manager.find_user_by_email(email)
    return None

def save_user_booking(user_id: str, booking_data: Dict) -> str:
    """Lưu booking cho user"""
    return user_data_manager.add_booking(user_id, booking_data)