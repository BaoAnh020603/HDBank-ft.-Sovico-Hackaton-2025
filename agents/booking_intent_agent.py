"""
Booking Intent Agent - Xử lý ý định đặt vé
"""

from typing import Dict, Any
from .booking_agent import booking_agent

class BookingIntentAgent:
    """Agent xử lý ý định đặt vé từ user"""
    
    def __init__(self):
        self.name = "BookingIntentAgent"
        self.booking_state = {}  # Lưu trạng thái đặt vé
    
    def detect_booking_intent(self, user_message: str, context: Dict = None) -> Dict[str, Any]:
        """Phát hiện ý định đặt vé từ tin nhắn user"""
        
        message_lower = user_message.lower()
        
        # Các từ khóa đặt vé
        booking_keywords = [
            "đặt", "book", "booking", "đặt vé", "đặt chuyến", 
            "đặt ngay", "đặt đi", "mua vé", "chọn chuyến"
        ]
        
        # Kiểm tra ý định đặt vé
        has_booking_intent = any(keyword in message_lower for keyword in booking_keywords)
        
        if has_booking_intent:
            # Trích xuất thông tin chuyến bay từ context hoặc message
            flight_info = self._extract_flight_info(user_message, context)
            
            return {
                "has_intent": True,
                "intent_type": "book_flight",
                "flight_info": flight_info,
                "next_step": "collect_passenger_info"
            }
        
        return {
            "has_intent": False,
            "intent_type": None
        }
    
    def _extract_flight_info(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """Trích xuất thông tin chuyến bay từ message hoặc context"""
        
        # Mặc định lấy chuyến bay rẻ nhất HCM-HN hôm nay
        from data.mock_data_loader import get_mock_data_loader
        
        loader = get_mock_data_loader()
        flights = loader.get_flights_by_route_and_date("Ho Chi Minh City", "Hanoi", "hôm nay")
        
        if flights:
            cheapest = min(flights, key=lambda x: x['price'])
            return {
                "flight_id": cheapest["flight_id"],
                "airline": cheapest["airline"],
                "from_city": cheapest["from_city"],
                "to_city": cheapest["to_city"],
                "date": cheapest["date"],
                "time": cheapest["time"],
                "price": cheapest["price"],
                "duration": cheapest.get("duration", "2h05m")
            }
        
        return {}
    
    def start_booking_process(self, flight_info: Dict[str, Any]) -> Dict[str, Any]:
        """Bắt đầu quy trình đặt vé"""
        
        # Nếu flight_info là kết quả từ SearchAgent, trích xuất flight data
        actual_flight = None
        if flight_info and isinstance(flight_info, dict):
            if 'data' in flight_info and 'flights' in flight_info['data']:
                # Lấy flight rẻ nhất từ kết quả search
                flights = flight_info['data']['flights']
                if flights:
                    actual_flight = min(flights, key=lambda x: x.get('price', 999999999))
            elif 'flight_id' in flight_info:
                # Đã là flight data
                actual_flight = flight_info
        
        # Nếu không có flight data, lấy mặc định
        if not actual_flight:
            try:
                from data.mock_data_loader import get_mock_data_loader
                loader = get_mock_data_loader()
                flights = loader.get_flights_by_route_and_date("Ho Chi Minh City", "Hanoi", "hôm nay")
                if flights:
                    actual_flight = min(flights, key=lambda x: x.get('price', 999999999))
            except:
                pass
        
        if not actual_flight:
            return {
                "success": False,
                "message": "Không tìm thấy thông tin chuyến bay để đặt."
            }
        
        # Lấy thông tin flight động
        flight_id = actual_flight.get('flight_id', 'VJ112')
        airline = actual_flight.get('airline', 'VietJet Air')
        from_city = actual_flight.get('from_city', 'Ho Chi Minh City')
        to_city = actual_flight.get('to_city', 'Hanoi')
        date = actual_flight.get('date', '2025-01-20')
        time = actual_flight.get('time', '06:00')
        price = actual_flight.get('price', 1665967)
        
        # Tạo session đặt vé
        session_id = f"booking_{flight_id}_{hash(str(actual_flight)) % 10000}"
        
        self.booking_state[session_id] = {
            "step": "request_contact_info",
            "flight_info": actual_flight,
            "passenger_info": None,
            "contact_info": None
        }
        
        message = f"""
🛫 **ĐẶT VÉ MÁY BAY**

Bạn đã chọn:
✈️ {airline} {flight_id}
📍 {from_city} → {to_city}
📅 {date} lúc {time}
💰 {price:,} VNĐ

📱 **Để tiếp tục đặt vé, vui lòng cung cấp số điện thoại:**
(Chúng tôi sẽ kiểm tra thông tin khách hàng có sẵn)
""".strip()
        
        return {
            "success": True,
            "session_id": session_id,
            "message": message,
            "next_step": "collect_phone"
        }
    
    def process_phone_input(self, session_id: str, phone: str) -> Dict[str, Any]:
        """Xử lý input số điện thoại"""
        
        if session_id not in self.booking_state:
            return {
                "success": False,
                "message": "Session đặt vé không hợp lệ. Vui lòng bắt đầu lại."
            }
        
        # Chuẩn hóa số điện thoại
        phone = phone.strip().replace(" ", "").replace("-", "")
        
        if not phone.startswith("0") or len(phone) != 10:
            return {
                "success": False,
                "message": "Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại 10 số bắt đầu bằng 0."
            }
        
        # Kiểm tra thông tin user
        confirmation = booking_agent.prepare_booking_confirmation(phone)
        
        # Cập nhật session
        self.booking_state[session_id]["phone"] = phone
        self.booking_state[session_id]["user_confirmation"] = confirmation
        self.booking_state[session_id]["step"] = "confirm_user_info"
        
        return {
            "success": True,
            "message": confirmation["message"],
            "user_type": confirmation["user_type"],
            "needs_confirmation": confirmation.get("needs_confirmation", False),
            "needs_info": confirmation.get("needs_info", [])
        }
    
    def process_user_confirmation(self, session_id: str, confirmation: str) -> Dict[str, Any]:
        """Xử lý xác nhận thông tin user"""
        
        if session_id not in self.booking_state:
            return {
                "success": False,
                "message": "Session không hợp lệ."
            }
        
        session = self.booking_state[session_id]
        confirmation_lower = confirmation.lower().strip()
        
        if confirmation_lower in ["đúng", "ok", "yes", "correct", "chính xác"]:
            # User xác nhận thông tin đúng
            user_data = session["user_confirmation"]["user_data"]
            
            # Yêu cầu thông tin bổ sung
            additional_info_msg = booking_agent.request_additional_info(user_data)
            
            session["step"] = "collect_additional_info"
            
            return {
                "success": True,
                "message": additional_info_msg,
                "next_step": "collect_cccd_sms"
            }
        
        elif confirmation_lower in ["sai", "sửa", "no", "incorrect", "chỉnh sửa"]:
            # User muốn sửa thông tin
            return {
                "success": True,
                "message": """
📝 **NHẬP THÔNG TIN MỚI**

Vui lòng cung cấp:
1. Họ tên đầy đủ
2. Số CMND/CCCD  
3. Email
4. Địa chỉ

Ví dụ: "Nguyễn Văn A, 123456789012, email@gmail.com, 123 Nguyễn Huệ Q1 HCM"
""".strip(),
                "next_step": "collect_new_info"
            }
        
        else:
            return {
                "success": False,
                "message": "Vui lòng trả lời 'Đúng' hoặc 'Sửa' để tiếp tục."
            }
    
    def process_additional_info(self, session_id: str, info_text: str) -> Dict[str, Any]:
        """Xử lý thông tin bổ sung (CCCD + SMS)"""
        
        if session_id not in self.booking_state:
            return {
                "success": False,
                "message": "Session không hợp lệ."
            }
        
        session = self.booking_state[session_id]
        
        # Parse thông tin CCCD và SMS phone - linh hoạt hơn
        info_lower = info_text.lower().strip()
        cccd = None
        sms_phone = None
        
        # Tìm CCCD (12-15 số)
        import re
        cccd_patterns = [
            r'cccd[:\s]*([0-9]{12,15})',
            r'cmnd[:\s]*([0-9]{12,15})',
            r'([0-9]{12,15})'  # Fallback: số dài 12-15 chữ số
        ]
        
        for pattern in cccd_patterns:
            match = re.search(pattern, info_lower)
            if match:
                cccd = match.group(1)
                break
        
        # Tìm SMS phone (10 số bắt đầu bằng 0)
        sms_patterns = [
            r'sms[:\s]*(0[0-9]{9})',
            r'điện thoại[:\s]*(0[0-9]{9})',
            r'phone[:\s]*(0[0-9]{9})',
            r'(0[0-9]{9})'  # Fallback: số điện thoại
        ]
        
        for pattern in sms_patterns:
            match = re.search(pattern, info_lower)
            if match:
                sms_phone = match.group(1)
                break
        
        # Nếu chỉ có CCCD, dùng SĐT hiện tại làm SMS
        if cccd and not sms_phone:
            sms_phone = session.get("phone", "")
        
        if not cccd:
            return {
                "success": False,
                "message": "❌ Vui lòng cung cấp số CCCD (12-15 số). Ví dụ: 123456789012345"
            }
        
        # Lưu thông tin và chuyển sang bước gửi SMS
        session["cccd"] = cccd
        session["sms_phone"] = sms_phone or session.get("phone", "")
        session["step"] = "send_sms"
        
        # Gửi SMS xác thực
        flight_info = session["flight_info"]
        date_str = flight_info.get('date', '22/09/2025').replace('/', '')
        flight_id = flight_info.get('flight_id', 'VJ112')
        booking_ref = f"SOVICO{date_str}{flight_id}"
        
        final_sms_phone = sms_phone or session.get("phone", "")
        sms_result = booking_agent.initiate_payment_verification(final_sms_phone, booking_ref)
        
        session["sms_code"] = sms_result.get("sms_code")  # Lưu để test
        session["booking_ref"] = booking_ref
        session["step"] = "verify_sms"
        
        # Thêm mã SMS vào message để test
        test_message = sms_result["message"]
        if sms_result.get("sms_code"):
            test_message += f"\n\n📝 **Mã test:** {sms_result['sms_code']}"
        
        return {
            "success": True,
            "message": test_message,
            "next_step": "verify_sms_code"
        }
    
    def process_sms_verification(self, session_id: str, sms_code: str) -> Dict[str, Any]:
        """Xử lý xác thực SMS"""
        
        if session_id not in self.booking_state:
            return {
                "success": False,
                "message": "Session không hợp lệ."
            }
        
        session = self.booking_state[session_id]
        sms_phone = session.get("sms_phone")
        
        if not sms_phone:
            return {
                "success": False,
                "message": "Không tìm thấy thông tin SMS."
            }
        
        # Xác thực SMS
        verify_result = booking_agent.verify_payment_code(sms_phone, sms_code, session_id)
        
        if verify_result["success"]:
            # Thanh toán thành công - có upselling
            session["step"] = "completed"
            
            return {
                "success": True,
                "message": verify_result["message"],
                "upsell_services": verify_result.get("upsell_services", []),
                "confirmation_code": verify_result.get("confirmation_code"),
                "completed": True
            }
        else:
            return {
                "success": False,
                "message": verify_result["error"],
                "attempts_left": verify_result.get("attempts_left")
            }
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Lấy thông tin session"""
        return self.booking_state.get(session_id, {})

# Global instance
booking_intent_agent = BookingIntentAgent()