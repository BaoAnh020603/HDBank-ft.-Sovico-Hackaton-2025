"""
Verification Agent - Xử lý xác thực SMS và thông tin
"""

import random
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class VerificationAgent:
    """Agent xử lý xác thực SMS và verification"""
    
    def __init__(self):
        self.name = "VerificationAgent"
        self.sms_codes = {}  # Lưu mã SMS tạm thời
        
    def send_sms_code(self, phone: str, purpose: str = "payment") -> Dict[str, Any]:
        """Gửi mã SMS xác thực"""
        
        # Tạo mã 6 số
        code = f"{random.randint(100000, 999999)}"
        
        # Lưu mã với thời hạn 5 phút
        self.sms_codes[phone] = {
            "code": code,
            "purpose": purpose,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=5),
            "attempts": 0
        }
        
        # Mock gửi SMS
        return {
            "success": True,
            "message": f"📱 Mã xác thực đã được gửi đến {phone[-4:].rjust(len(phone), '*')}",
            "code": code,  # Chỉ để test, thực tế không trả về
            "expires_in": 300  # 5 phút
        }
    
    def verify_sms_code(self, phone: str, input_code: str) -> Dict[str, Any]:
        """Xác thực mã SMS"""
        
        if phone not in self.sms_codes:
            return {
                "success": False,
                "error": "Không tìm thấy mã xác thực. Vui lòng yêu cầu gửi lại."
            }
        
        sms_data = self.sms_codes[phone]
        
        # Kiểm tra hết hạn
        if datetime.now() > sms_data["expires_at"]:
            del self.sms_codes[phone]
            return {
                "success": False,
                "error": "Mã xác thực đã hết hạn. Vui lòng yêu cầu gửi lại."
            }
        
        # Kiểm tra số lần thử
        sms_data["attempts"] += 1
        if sms_data["attempts"] > 3:
            del self.sms_codes[phone]
            return {
                "success": False,
                "error": "Đã nhập sai quá 3 lần. Vui lòng yêu cầu gửi lại mã mới."
            }
        
        # Kiểm tra mã
        if input_code != sms_data["code"]:
            return {
                "success": False,
                "error": f"Mã xác thực không đúng. Còn {3 - sms_data['attempts']} lần thử.",
                "attempts_left": 3 - sms_data["attempts"]
            }
        
        # Xác thực thành công
        del self.sms_codes[phone]
        return {
            "success": True,
            "message": "✅ Xác thực thành công!",
            "verified_at": datetime.now().isoformat()
        }
    
    def confirm_user_info(self, user_data: Dict[str, Any], additional_info: Dict[str, Any] = None) -> str:
        """Tạo message xác nhận thông tin user"""
        
        message = f"""
📋 **XÁC NHẬN THÔNG TIN**

👤 **Thông tin hành khách:**
- Họ tên: {user_data.get('full_name', 'N/A')}
- CMND/CCCD: {user_data.get('id_number', 'N/A')}
- Điện thoại: {user_data.get('phone', 'N/A')}
- Email: {user_data.get('email', 'N/A')}
"""
        
        if additional_info:
            if additional_info.get('cccd'):
                message += f"- CCCD mới: {additional_info['cccd']}\n"
            if additional_info.get('sms_phone'):
                message += f"- SĐT nhận SMS: {additional_info['sms_phone']}\n"
        
        message += "\n❓ **Thông tin trên có chính xác không?**\n"
        message += "Trả lời: 'Đúng' để tiếp tục hoặc 'Sửa' để chỉnh sửa"
        
        return message.strip()

# Global instance
verification_agent = VerificationAgent()