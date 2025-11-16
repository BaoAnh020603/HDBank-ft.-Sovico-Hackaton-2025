"""
Booking Agent - Xử lý đặt vé và booking
"""

from typing import Dict, Any, List
from datetime import datetime
import uuid
from .payment_agent import payment_agent
from .verification_agent import verification_agent
from .upselling_agent import upsell_agent
from data.mock_user_data import find_user_by_phone, find_user_by_email, create_mock_user, add_mock_booking, get_user_bookings, get_user_stats, MOCK_USERS

class BookingAgent:
    """Agent xử lý booking và tích hợp với payment"""
    
    def __init__(self):
        self.name = "BookingAgent"
        
    def create_booking(self, service_data: Dict[str, Any], passenger_info: List[Dict], contact_info: Dict) -> Dict[str, Any]:
        """Tạo booking mới và quản lý user"""
        
        # Validate input
        if not self._validate_input(service_data, passenger_info, contact_info):
            return {
                "success": False,
                "error": "Thông tin không hợp lệ"
            }
        
        # Tìm hoặc tạo user (mock)
        user = self._get_or_create_mock_user(contact_info, passenger_info[0])
        user_id = user["user_id"]
        
        # Tạo booking data
        booking_data = {
            "service_type": service_data["type"],  # "flight" hoặc "hotel"
            "service_id": service_data["service_id"],
            "base_price": service_data["price"],
            "passenger_info": passenger_info,
            "contact_info": contact_info,
            "booking_details": service_data,
            "created_at": datetime.now().isoformat()
        }
        
        # Xử lý thanh toán
        payment_result = payment_agent.process_payment(booking_data)
        
        if payment_result["success"]:
            # Lưu booking vào user data
            booking_record = {
                "service_type": service_data["type"],
                "service_id": service_data["service_id"],
                "booking_reference": payment_result["booking_reference"],
                "total_amount": payment_result["total_amount"],
                "payment_status": "pending",
                "booking_status": "pending",
                "booking_details": booking_data
            }
            
            booking_id = add_mock_booking(user_id, booking_record)
            
            return {
                "success": True,
                "user_id": user_id,
                "booking_id": booking_id,
                "booking_data": booking_data,
                "payment_session": payment_result,
                "message": f"✅ Đã tạo booking thành công! Mã tham chiếu: {payment_result['booking_reference']}"
            }
        else:
            return {
                "success": False,
                "error": payment_result["error"]
            }
    
    def confirm_booking_payment(self, session_id: str, payment_method: str, payment_details: Dict) -> Dict[str, Any]:
        """Xác nhận thanh toán cho booking"""
        
        payment_result = payment_agent.confirm_payment(session_id, payment_method, payment_details)
        
        if payment_result["success"]:
            return {
                "success": True,
                "confirmation": payment_result["booking_confirmation"],
                "transaction_id": payment_result["transaction_id"],
                "message": payment_result["message"]
            }
        else:
            return {
                "success": False,
                "error": payment_result["error"]
            }
    
    def book_flight(self, flight_data: Dict, passengers: List[Dict], contact: Dict) -> Dict[str, Any]:
        """Đặt vé máy bay"""
        
        service_data = {
            "type": "flight",
            "service_id": flight_data["flight_id"],
            "price": flight_data["price"],
            "flight_details": {
                "flight_id": flight_data["flight_id"],
                "airline": flight_data["airline"],
                "from_city": flight_data["from_city"],
                "to_city": flight_data["to_city"],
                "date": flight_data["date"],
                "time": flight_data["time"],
                "duration": flight_data.get("duration", "2h00m")
            }
        }
        
        return self.create_booking(service_data, passengers, contact)
    
    def book_hotel(self, hotel_data: Dict, guest_info: List[Dict], contact: Dict) -> Dict[str, Any]:
        """Đặt khách sạn"""
        
        service_data = {
            "type": "hotel",
            "service_id": hotel_data["service_id"],
            "price": hotel_data["price_per_night"],
            "nights": hotel_data.get("nights", 1),
            "rooms": hotel_data.get("rooms", 1),
            "hotel_details": {
                "name": hotel_data["name"],
                "location": hotel_data["location"],
                "check_in": hotel_data.get("check_in"),
                "check_out": hotel_data.get("check_out"),
                "room_type": hotel_data.get("type", "Standard")
            }
        }
        
        return self.create_booking(service_data, guest_info, contact)
    
    def _validate_input(self, service_data: Dict, passenger_info: List, contact_info: Dict) -> bool:
        """Validate input data"""
        
        # Validate service data
        if not service_data or "type" not in service_data or "price" not in service_data:
            return False
        
        # Validate passenger info
        if not passenger_info or len(passenger_info) == 0:
            return False
        
        for passenger in passenger_info:
            required_fields = ["full_name", "id_number", "phone"]
            if not all(field in passenger for field in required_fields):
                return False
        
        # Validate contact info
        if not contact_info or "email" not in contact_info or "phone" not in contact_info:
            return False
        
        return True
    
    def get_booking_summary(self, booking_data: Dict, payment_session: Dict) -> str:
        """Tạo tóm tắt booking cho user"""
        
        service_type = booking_data["service_type"]
        cost_breakdown = payment_session["cost_breakdown"]
        
        if service_type == "flight":
            details = booking_data["booking_details"]["flight_details"]
            summary = f"""
🛫 **THÔNG TIN CHUYẾN BAY**
- Chuyến bay: {details['airline']} {details['flight_id']}
- Tuyến: {details['from_city']} → {details['to_city']}
- Ngày giờ: {details['date']} lúc {details['time']}
- Thời gian bay: {details['duration']}

👥 **HÀNH KHÁCH** ({len(booking_data['passenger_info'])} người)
"""
            for i, passenger in enumerate(booking_data['passenger_info'], 1):
                summary += f"- {i}. {passenger['full_name']} (CMND: {passenger['id_number']})\n"
            
        elif service_type == "hotel":
            details = booking_data["booking_details"]["hotel_details"]
            summary = f"""
🏨 **THÔNG TIN KHÁCH SẠN**
- Khách sạn: {details['name']}
- Địa điểm: {details['location']}
- Check-in: {details['check_in']}
- Check-out: {details['check_out']}
- Loại phòng: {details['room_type']}

👥 **KHÁCH** ({len(booking_data['passenger_info'])} người)
"""
            for i, guest in enumerate(booking_data['passenger_info'], 1):
                summary += f"- {i}. {guest['full_name']}\n"
        
        summary += f"""
💰 **CHI PHÍ**
"""
        for item, amount in cost_breakdown["breakdown"].items():
            summary += f"- {item}: {amount}\n"
        
        summary += f"""
📞 **LIÊN HỆ**
- Email: {booking_data['contact_info']['email']}
- Điện thoại: {booking_data['contact_info']['phone']}

⏰ **Thời hạn thanh toán:** 15 phút
🔗 **Mã tham chiếu:** {payment_session['booking_reference']}
"""
        
        return summary.strip()
    
    def _get_or_create_mock_user(self, contact_info: Dict, primary_passenger: Dict) -> Dict[str, Any]:
        """Tìm hoặc tạo mock user"""
        
        phone = contact_info.get("phone")
        email = contact_info.get("email")
        
        # Tìm user cũ
        existing_user = find_user_by_phone(phone) or find_user_by_email(email)
        if existing_user:
            return existing_user
        
        # Tạo user mới
        user_info = {
            "full_name": primary_passenger.get("full_name", ""),
            "email": email,
            "phone": phone,
            "id_number": primary_passenger.get("id_number", "")
        }
        
        user_id = create_mock_user(user_info)
        return MOCK_USERS[user_id]
    
    def get_user_booking_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Lấy lịch sử booking của user"""
        return get_user_bookings(user_id)
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Lấy thống kê user"""
        return get_user_stats(user_id)
    
    def prepare_booking_confirmation(self, phone: str, email: str = None) -> Dict[str, Any]:
        """Chuẩn bị xác nhận booking - tự động lấy thông tin user"""
        
        # Tìm user theo phone/email
        user = find_user_by_phone(phone) or (find_user_by_email(email) if email else None)
        
        if user:
            # User cũ - hiển thị thông tin để xác nhận
            confirmation_msg = verification_agent.confirm_user_info(user)
            
            return {
                "success": True,
                "user_type": "existing",
                "user_data": user,
                "message": f"👋 Chào lại {user['full_name']}! ({user['total_bookings']} booking, {user['loyalty_points']} điểm)\n\n{confirmation_msg}",
                "needs_confirmation": True
            }
        else:
            # User mới - cần nhập thông tin
            return {
                "success": True,
                "user_type": "new",
                "message": "🎆 Chào mừng bạn đến với SOVICO!\n\n📝 Vui lòng cung cấp thông tin:\n- Họ tên đầy đủ\n- Số CMND/CCCD\n- Email\n- Địa chỉ",
                "needs_info": ["full_name", "id_number", "email", "address"]
            }
    
    def request_additional_info(self, user_data: Dict[str, Any]) -> str:
        """Yêu cầu thông tin bổ sung (CCCD và SMS)"""
        
        return f"""
📝 **THÔNG TIN BỔ SUNG**

Vui lòng cung cấp thêm:
1️⃣ **Số CCCD mới nhất** (nếu khác với CMND cũ: {user_data.get('id_number', 'N/A')})
2️⃣ **Số điện thoại nhận SMS** xác thực thanh toán

📱 SMS sẽ được gửi để xác thực giao dịch.
""".strip()
    
    def initiate_payment_verification(self, phone: str, booking_reference: str) -> Dict[str, Any]:
        """Khởi tạo xác thực thanh toán qua SMS"""
        
        # Gửi mã SMS
        sms_result = verification_agent.send_sms_code(phone, "payment")
        
        if sms_result["success"]:
            return {
                "success": True,
                "message": f"""
💳 **XÁC THỰC THANH TOÁN**

{sms_result['message']}

🔐 Vui lòng nhập mã 6 số để xác nhận thanh toán cho booking: {booking_reference}

⏰ Mã có hiệu lực trong 5 phút
""".strip(),
                "sms_code": sms_result.get("code"),  # Chỉ để test
                "expires_in": sms_result["expires_in"]
            }
        else:
            return {
                "success": False,
                "error": "Không thể gửi SMS. Vui lòng thử lại."
            }
    
    def verify_payment_code(self, phone: str, code: str, booking_id: str) -> Dict[str, Any]:
        """Xác thực mã thanh toán"""
        
        verify_result = verification_agent.verify_sms_code(phone, code)
        
        if verify_result["success"]:
            # Cập nhật trạng thái booking thành completed
            # (Trong thực tế sẽ cập nhật database)
            
            # Lấy gợi ý dịch vụ bổ sung
            upsell_suggestions = self._get_upsell_suggestions(booking_id)
            
            success_message = f"""
🎉 **THANH TOÁN THÀNH CÔNG!**

✅ Xác thực hoàn tất
🎫 Mã xác nhận: CONF{booking_id[-8:].upper()}
📧 Email xác nhận đã gửi

📝 **HƯỚng dẫn:**
- Có mặt tại sân bay trước 2 tiếng
- Mang theo CMND/CCCD và mã xác nhận
- Check-in online: vietjetair.com
""".strip()
            
            if upsell_suggestions:
                success_message += f"\n\n{upsell_suggestions['message']}"
            
            return {
                "success": True,
                "message": success_message,
                "confirmation_code": f"CONF{booking_id[-8:].upper()}",
                "verified_at": verify_result["verified_at"],
                "upsell_services": upsell_suggestions.get("services", []) if upsell_suggestions else []
            }
        else:
            return {
                "success": False,
                "error": verify_result["error"],
                "attempts_left": verify_result.get("attempts_left")
            }
    
    def _get_upsell_suggestions(self, booking_id: str) -> Dict[str, Any]:
        """Lấy gợi ý dịch vụ bổ sung dựa trên booking"""
        
        # Mock booking data - trong thực tế sẽ lấy từ database
        mock_booking_data = {
            "service_type": "flight",
            "booking_details": {
                "flight_details": {
                    "to_city": "Hanoi",
                    "from_city": "Ho Chi Minh City"
                }
            }
        }
        
        return upsell_agent.get_travel_services_suggestions(mock_booking_data)
    
    def get_service_details(self, service_id: str) -> Dict[str, Any]:
        """Lấy chi tiết dịch vụ theo ID"""
        
        # Lấy danh sách dịch vụ (mock)
        mock_booking_data = {
            "service_type": "flight",
            "booking_details": {
                "flight_details": {
                    "to_city": "Hanoi"
                }
            }
        }
        
        suggestions = upsell_agent.get_travel_services_suggestions(mock_booking_data)
        return upsell_agent.get_service_details(service_id, suggestions.get("services", []))
    
    def book_additional_service(self, service_id: str, service_details: Dict[str, Any]) -> Dict[str, Any]:
        """\u0110ặt dịch vụ bổ sung"""
        
        # Validate service details
        required_fields = {
            "hotel": ["check_in", "check_out", "guests", "rooms"],
            "transfer": ["pickup_time", "pickup_address"],
            "tour": ["tour_date", "participants"],
            "insurance": ["confirm"]
        }
        
        service_info = self.get_service_details(service_id)
        if not service_info["success"]:
            return {
                "success": False,
                "error": "Không tìm thấy dịch vụ"
            }
        
        service = service_info["service"]
        service_type = service["type"]
        
        # Kiểm tra thông tin cần thiết
        missing_fields = []
        for field in required_fields.get(service_type, []):
            if field not in service_details:
                missing_fields.append(field)
        
        if missing_fields:
            return {
                "success": False,
                "error": f"Thiếu thông tin: {', '.join(missing_fields)}",
                "missing_fields": missing_fields
            }
        
        # Tạo booking cho dịch vụ bổ sung
        additional_booking = {
            "service_id": service_id,
            "service_name": service["name"],
            "service_type": service_type,
            "price": service["price"],
            "details": service_details,
            "booking_reference": f"SOVICO{datetime.now().strftime('%Y%m%d')}{service_id[-6:].upper()}",
            "status": "confirmed"
        }
        
        return {
            "success": True,
            "booking": additional_booking,
            "message": f"✅ Đặt {service['name']} thành công!\n🔗 Mã tham chiếu: {additional_booking['booking_reference']}"
        }

# Global instance
booking_agent = BookingAgent()