"""
Upselling Agent V2 - Gợi ý dịch vụ bổ sung SOVICO với mock data thật
"""

from typing import Dict, Any, List
import random
from .sovico_data import SovicoDataProvider

class UpsellAgent:
    """Agent gợi ý dịch vụ bổ sung SOVICO"""
    
    def __init__(self):
        self.name = "UpsellAgent"
        
    def get_travel_services_suggestions(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gợi ý dịch vụ du lịch dựa trên booking"""
        
        service_type = booking_data.get("service_type", "flight")
        destination = self._get_destination(booking_data)
        
        if service_type == "flight":
            return self._get_flight_upsell_services(destination, booking_data)
        elif service_type == "hotel":
            return self._get_hotel_upsell_services(destination, booking_data)
        
        return {"services": [], "message": ""}
    
    def _get_destination(self, booking_data: Dict[str, Any]) -> str:
        """Lấy điểm đến từ booking data"""
        if booking_data.get("service_type") == "flight":
            details = booking_data.get("booking_details", {}).get("flight_details", {})
            return details.get("to_city", "")
        elif booking_data.get("service_type") == "hotel":
            details = booking_data.get("booking_details", {}).get("hotel_details", {})
            return details.get("location", "")
        return ""
    
    def _get_flight_upsell_services(self, destination: str, booking_data: Dict) -> Dict[str, Any]:
        """Gợi ý dịch vụ cho chuyến bay"""
        
        services = []
        
        # Khách sạn SOVICO
        hotels = SovicoDataProvider.get_hotels(destination)
        if hotels:
            services.extend(hotels[:2])  # Lấy 2 khách sạn đầu
        
        # Xe đưa đón SOVICO
        transfer = SovicoDataProvider.get_transfer(destination)
        if transfer:
            services.append(transfer)
        
        # Tour SOVICO
        tours = SovicoDataProvider.get_tours(destination)
        if tours:
            services.extend(tours[:1])  # Lấy 1 tour
        
        # Bảo hiểm SOVICO
        insurance = SovicoDataProvider.get_insurance()
        services.append(insurance)
        
        message = self._create_upsell_message(destination, "flight")
        
        return {
            "services": services,
            "message": message,
            "destination": destination
        }
    
    def _get_hotel_upsell_services(self, destination: str, booking_data: Dict) -> Dict[str, Any]:
        """Gợi ý dịch vụ cho khách sạn"""
        
        services = []
        
        # Xe đưa đón
        transfer = SovicoDataProvider.get_transfer(destination)
        services.append(transfer)
        
        # Tour
        tours = SovicoDataProvider.get_tours(destination)
        if tours:
            services.extend(tours[:2])
        
        # Bảo hiểm
        insurance = SovicoDataProvider.get_insurance()
        services.append(insurance)
        
        message = self._create_upsell_message(destination, "hotel")
        
        return {
            "services": services,
            "message": message,
            "destination": destination
        }
    
    def _create_upsell_message(self, destination: str, service_type: str) -> str:
        """Tạo message gợi ý dịch vụ"""
        
        if service_type == "flight":
            return f"""
🎉 **CHÚC MỪNG ĐẶT VÉ THÀNH CÔNG!**

🌟 **DỊCH VỤ BỔ SUNG TẠI {destination.upper()}**

SOVICO có thể hỗ trợ thêm cho chuyến đi của bạn:

🏨 **Khách sạn SOVICO** - Ưu đãi đặc biệt cho khách VietJet
🚗 **Xe đưa đón sân bay** - Tiện lợi, an toàn, đúng giờ  
🎯 **Tour du lịch** - Khám phá điểm đến với hướng dẫn viên chuyên nghiệp
🛡️ **Bảo hiểm SOVICO Care** - An tâm tuyệt đối cho chuyến đi

💝 **Ưu đãi combo:** Giảm 15-30% khi đặt kèm vé VietJet!

Bạn có muốn tìm hiểu thêm dịch vụ nào không?
""".strip()
        
        return "Bạn có cần thêm dịch vụ du lịch SOVICO nào khác không?"
    
    def get_service_details(self, service_id: str, services_list: List[Dict]) -> Dict[str, Any]:
        """Lấy chi tiết dịch vụ"""
        
        for service in services_list:
            if service["id"] == service_id:
                return {
                    "success": True,
                    "service": service,
                    "booking_info": self._create_service_booking_info(service)
                }
        
        return {
            "success": False,
            "error": "Không tìm thấy dịch vụ"
        }
    
    def _create_service_booking_info(self, service: Dict[str, Any]) -> str:
        """Tạo thông tin booking cho dịch vụ"""
        
        service_type = service["type"]
        name = service["name"]
        price = service["price"]
        
        if service_type == "hotel":
            return f"""
🏨 **{name}**
⭐ {service.get('rating', 4)} sao
💰 {price:,} VNĐ/{service['unit']}
🎁 {service.get('discount', 'Ưu đãi đặc biệt')}
📍 {service.get('location', 'Vị trí thuận lợi')}

📝 Bạn muốn đặt từ ngày nào đến ngày nào?
👥 Số người: ? | Số phòng: ?
""".strip()
            
        elif service_type == "transfer":
            return f"""
🚗 **{name}**
💰 {price:,} VNĐ/{service['unit']}
🎁 {service.get('discount', 'Ưu đãi combo')}

✨ **Tính năng:**
{chr(10).join(f"• {feature}" for feature in service.get('features', ['Dịch vụ chuyên nghiệp']))}

📝 Bạn cần đưa đón lúc mấy giờ?
📍 Địa chỉ đón: ?
""".strip()
            
        elif service_type == "tour":
            return f"""
🎯 **{name}**
⏰ {service.get('duration', '1 ngày')}
💰 {price:,} VNĐ/{service['unit']}

📋 **Bao gồm:**
{chr(10).join(f"• {item}" for item in service.get('includes', ['Hướng dẫn viên', 'Xe đưa đón']))}

📅 Bạn muốn tham gia tour ngày nào?
👥 Số người tham gia: ?
""".strip()
            
        elif service_type == "insurance":
            return f"""
🛡️ **{name}**
💰 {price:,} VNĐ/{service['unit']}
🏥 Bảo hiểm: {service.get('coverage', '5 tỷ VNĐ')}

🎯 **Quyền lợi:**
{chr(10).join(f"• {benefit}" for benefit in service.get('benefits', ['Bảo hiểm toàn diện']))}

✅ Bạn có muốn mua bảo hiểm này không?
""".strip()
        
        return f"Chi tiết dịch vụ {name} - {price:,} VNĐ"

# Global instance
upsell_agent = UpsellAgent()