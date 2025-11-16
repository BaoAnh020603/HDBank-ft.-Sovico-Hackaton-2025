"""
Payment Agent - Xử lý thanh toán cho booking
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import uuid
import json

class PaymentAgent:
    """Agent xử lý thanh toán"""
    
    def __init__(self):
        self.name = "PaymentAgent"
        self.supported_methods = ["momo", "zalopay", "vnpay", "banking", "visa", "mastercard"]
        
    def process_payment(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Xử lý thanh toán cho booking"""
        
        # Validate booking data
        if not self._validate_booking(booking_data):
            return {
                "success": False,
                "error": "Thông tin booking không hợp lệ"
            }
        
        # Tạo payment session
        payment_session = self._create_payment_session(booking_data)
        
        # Tính toán chi phí
        cost_breakdown = self._calculate_costs(booking_data)
        
        return {
            "success": True,
            "payment_session_id": payment_session["session_id"],
            "total_amount": cost_breakdown["total"],
            "cost_breakdown": cost_breakdown,
            "payment_methods": self._get_available_methods(),
            "expires_at": payment_session["expires_at"],
            "booking_reference": payment_session["booking_ref"]
        }
    
    def confirm_payment(self, session_id: str, payment_method: str, payment_details: Dict) -> Dict[str, Any]:
        """Xác nhận thanh toán"""
        
        # Validate payment method
        if payment_method not in self.supported_methods:
            return {
                "success": False,
                "error": f"Phương thức thanh toán {payment_method} không được hỗ trợ"
            }
        
        # Process payment based on method
        payment_result = self._process_payment_method(payment_method, payment_details)
        
        if payment_result["success"]:
            # Tạo booking confirmation
            booking_confirmation = self._create_booking_confirmation(session_id, payment_result)
            
            return {
                "success": True,
                "transaction_id": payment_result["transaction_id"],
                "booking_confirmation": booking_confirmation,
                "payment_status": "completed",
                "message": "🎉 Thanh toán thành công! Vé đã được đặt."
            }
        else:
            return {
                "success": False,
                "error": payment_result["error"],
                "payment_status": "failed"
            }
    
    def _validate_booking(self, booking_data: Dict) -> bool:
        """Validate thông tin booking"""
        required_fields = ["service_type", "service_id", "passenger_info", "contact_info"]
        
        for field in required_fields:
            if field not in booking_data:
                return False
        
        # Validate passenger info
        passenger_info = booking_data["passenger_info"]
        if not isinstance(passenger_info, list) or len(passenger_info) == 0:
            return False
        
        for passenger in passenger_info:
            if not all(key in passenger for key in ["full_name", "id_number", "phone"]):
                return False
        
        return True
    
    def _create_payment_session(self, booking_data: Dict) -> Dict[str, Any]:
        """Tạo payment session"""
        session_id = str(uuid.uuid4())
        booking_ref = f"SOVICO{datetime.now().strftime('%Y%m%d')}{session_id[:6].upper()}"
        expires_at = datetime.now() + timedelta(minutes=15)  # 15 phút để thanh toán
        
        return {
            "session_id": session_id,
            "booking_ref": booking_ref,
            "expires_at": expires_at.isoformat(),
            "booking_data": booking_data,
            "created_at": datetime.now().isoformat()
        }
    
    def _calculate_costs(self, booking_data: Dict) -> Dict[str, Any]:
        """Tính toán chi phí"""
        service_type = booking_data["service_type"]
        
        if service_type == "flight":
            return self._calculate_flight_costs(booking_data)
        elif service_type == "hotel":
            return self._calculate_hotel_costs(booking_data)
        else:
            return {"total": 0, "breakdown": {}}
    
    def _calculate_flight_costs(self, booking_data: Dict) -> Dict[str, Any]:
        """Tính chi phí vé máy bay"""
        base_price = booking_data.get("base_price", 0)
        passengers = len(booking_data["passenger_info"])
        
        # Chi phí cơ bản
        subtotal = base_price * passengers
        
        # Phí dịch vụ SOVICO (2%)
        service_fee = int(subtotal * 0.02)
        
        # Thuế và phí (đã bao gồm trong giá vé)
        taxes = int(subtotal * 0.1)
        
        # Bảo hiểm (tùy chọn)
        insurance = 0
        if booking_data.get("add_insurance", False):
            insurance = passengers * 50000  # 50k/người
        
        total = subtotal + service_fee + insurance
        
        return {
            "subtotal": subtotal,
            "service_fee": service_fee,
            "taxes": taxes,
            "insurance": insurance,
            "total": total,
            "passengers": passengers,
            "breakdown": {
                "Giá vé": f"{subtotal:,} VNĐ",
                "Phí dịch vụ SOVICO": f"{service_fee:,} VNĐ",
                "Bảo hiểm": f"{insurance:,} VNĐ" if insurance > 0 else "Không",
                "Tổng cộng": f"{total:,} VNĐ"
            }
        }
    
    def _calculate_hotel_costs(self, booking_data: Dict) -> Dict[str, Any]:
        """Tính chi phí khách sạn"""
        price_per_night = booking_data.get("price_per_night", 0)
        nights = booking_data.get("nights", 1)
        rooms = booking_data.get("rooms", 1)
        
        subtotal = price_per_night * nights * rooms
        service_fee = int(subtotal * 0.03)  # 3% cho hotel
        total = subtotal + service_fee
        
        return {
            "subtotal": subtotal,
            "service_fee": service_fee,
            "total": total,
            "breakdown": {
                "Phòng": f"{price_per_night:,} VNĐ x {nights} đêm x {rooms} phòng",
                "Phí dịch vụ": f"{service_fee:,} VNĐ",
                "Tổng cộng": f"{total:,} VNĐ"
            }
        }
    
    def _get_available_methods(self) -> List[Dict[str, Any]]:
        """Lấy danh sách phương thức thanh toán"""
        return [
            {"id": "momo", "name": "Ví MoMo", "icon": "🟣", "fee": 0},
            {"id": "zalopay", "name": "ZaloPay", "icon": "🔵", "fee": 0},
            {"id": "vnpay", "name": "VNPay", "icon": "🟠", "fee": 0},
            {"id": "banking", "name": "Chuyển khoản ngân hàng", "icon": "🏦", "fee": 0},
            {"id": "visa", "name": "Thẻ Visa", "icon": "💳", "fee": "1.5%"},
            {"id": "mastercard", "name": "Thẻ MasterCard", "icon": "💳", "fee": "1.5%"}
        ]
    
    def _process_payment_method(self, method: str, details: Dict) -> Dict[str, Any]:
        """Xử lý thanh toán theo phương thức"""
        
        # Mock payment processing - trong thực tế sẽ gọi API của payment gateway
        transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
        
        if method in ["momo", "zalopay", "vnpay"]:
            return self._process_ewallet(method, details, transaction_id)
        elif method == "banking":
            return self._process_banking(details, transaction_id)
        elif method in ["visa", "mastercard"]:
            return self._process_card(method, details, transaction_id)
        else:
            return {"success": False, "error": "Phương thức thanh toán không hỗ trợ"}
    
    def _process_ewallet(self, wallet_type: str, details: Dict, transaction_id: str) -> Dict[str, Any]:
        """Xử lý thanh toán ví điện tử"""
        phone = details.get("phone")
        amount = details.get("amount")
        
        if not phone or not amount:
            return {"success": False, "error": "Thiếu thông tin số điện thoại hoặc số tiền"}
        
        # Mock successful payment
        return {
            "success": True,
            "transaction_id": transaction_id,
            "payment_method": wallet_type,
            "amount": amount,
            "status": "completed",
            "gateway_response": f"Thanh toán {wallet_type} thành công"
        }
    
    def _process_banking(self, details: Dict, transaction_id: str) -> Dict[str, Any]:
        """Xử lý chuyển khoản ngân hàng"""
        bank_code = details.get("bank_code")
        account_number = details.get("account_number")
        amount = details.get("amount")
        
        if not all([bank_code, account_number, amount]):
            return {"success": False, "error": "Thiếu thông tin ngân hàng"}
        
        # Mock banking transfer
        return {
            "success": True,
            "transaction_id": transaction_id,
            "payment_method": "banking",
            "amount": amount,
            "status": "completed",
            "transfer_info": {
                "bank": bank_code,
                "account": account_number[-4:].rjust(len(account_number), '*'),
                "reference": transaction_id
            }
        }
    
    def _process_card(self, card_type: str, details: Dict, transaction_id: str) -> Dict[str, Any]:
        """Xử lý thanh toán thẻ"""
        card_number = details.get("card_number")
        expiry = details.get("expiry")
        cvv = details.get("cvv")
        amount = details.get("amount")
        
        if not all([card_number, expiry, cvv, amount]):
            return {"success": False, "error": "Thiếu thông tin thẻ"}
        
        # Mock card payment
        return {
            "success": True,
            "transaction_id": transaction_id,
            "payment_method": card_type,
            "amount": amount,
            "status": "completed",
            "card_info": {
                "last4": card_number[-4:],
                "type": card_type,
                "expiry": expiry
            }
        }
    
    def _create_booking_confirmation(self, session_id: str, payment_result: Dict) -> Dict[str, Any]:
        """Tạo xác nhận booking"""
        confirmation_code = f"CONF{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        
        return {
            "confirmation_code": confirmation_code,
            "booking_status": "confirmed",
            "payment_status": "completed",
            "transaction_id": payment_result["transaction_id"],
            "confirmed_at": datetime.now().isoformat(),
            "instructions": {
                "flight": "Vui lòng có mặt tại sân bay trước 2 tiếng. Mang theo CMND/CCCD và mã xác nhận.",
                "hotel": "Check-in từ 14:00, check-out trước 12:00. Mang theo CMND/CCCD và mã xác nhận."
            }
        }
    
    def get_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Kiểm tra trạng thái thanh toán"""
        # Mock status check
        return {
            "transaction_id": transaction_id,
            "status": "completed",
            "amount": 1665967,
            "payment_method": "momo",
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat()
        }

# Global instance
payment_agent = PaymentAgent()