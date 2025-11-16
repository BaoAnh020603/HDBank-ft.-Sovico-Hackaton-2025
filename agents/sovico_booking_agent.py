from typing import Dict, List, Any, Optional
from .smart_intent_agent import SmartIntentAgent
from .sovico_services_agent import SovicoServicesAgent
from .booking_intent_agent import BookingIntentAgent
import json

class SovicoBookingAgent:
    """Agent tổng hợp cho các dịch vụ Sovico"""
    
    def __init__(self, google_api_key: str = None):
        self.smart_intent = SmartIntentAgent()
        self.sovico_services = SovicoServicesAgent(api_key=google_api_key)
        self.booking_intent = BookingIntentAgent()
        
    def process_message(self, user_message: str, user_id: str) -> Dict[str, Any]:
        """Xử lý message cho dịch vụ Sovico"""
        
        intent_result = self.smart_intent.analyze_intent(user_message, user_id=user_id)
        
        if intent_result["intent"].startswith("request_"):
            return self._handle_service_request(user_message, intent_result, user_id)
        else:
            return self._handle_general_info(user_message, intent_result, user_id)
    
    def _handle_service_request(self, message: str, intent_result: Dict, user_id: str) -> Dict[str, Any]:
        """Xử lý yêu cầu dịch vụ Sovico"""
        
        service_type = intent_result["intent"].replace("request_", "")
        
        service_result = self.sovico_services.get_service_recommendations(
            service_type, {"message": message}
        )
        
        if service_result.get("status") == "success":
            return {
                "status": "service_provided",
                "response": service_result["response"],
                "service_type": service_type
            }
        
        return {
            "status": "service_error", 
            "response": "Có lỗi khi tìm dịch vụ. Thử lại được không?"
        }
    
    def _handle_general_info(self, message: str, intent_result: Dict, user_id: str) -> Dict[str, Any]:
        """Xử lý thông tin chung"""
        
        return {
            "status": "info_provided",
            "response": "Tôi là trợ lý Sovico, có thể giúp bạn:\n• 🏨 Khách sạn\n• 🚗 Xe đưa đón sân bay\n• 🎯 Tour du lịch\n• 🛡️ Bảo hiểm du lịch\n\nBạn cần dịch vụ nào?"
        }