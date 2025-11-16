"""
Upselling Agent - Gợi ý dịch vụ bổ sung của SOVICO
"""

from typing import Dict, Any, List
import random

class UpsellAgent:
    """Agent gợi ý dịch vụ bổ sung"""
    
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
        
        # Khách sạn tại điểm đến
        hotels = self._get_destination_hotels(destination)
        if hotels:
            services.extend(hotels)
        
        # Xe đưa đón sân bay
        airport_transfer = self._get_airport_transfer(destination)
        if airport_transfer:
            services.append(airport_transfer)
        
        # Tour du lịch
        tours = self._get_destination_tours(destination)
        if tours:
            services.extend(tours[:2])  # Chỉ lấy 2 tour
        
        # Bảo hiểm du lịch
        insurance = self._get_travel_insurance()
        services.append(insurance)
        
        message = self._create_upsell_message(destination, "flight")
        
        return {
            "services": services,
            "message": message,
            "destination": destination
        }
    
    def _get_destination_hotels(self, destination: str) -> List[Dict[str, Any]]:
        """Lấy khách sạn tại điểm đến"""
        
        # Chuẩn hóa tên điểm đến
        dest_normalized = destination.lower().replace(' ', '')
        
        hotel_data = {
            "hanoi": [
                {
                    "id": "hotel_hn_001",
                    "name": "Lotte Hotel Hanoi",
                    "type": "hotel",
                    "rating": 5,
                    "price": 2500000,
                    "unit": "đêm",
                    "description": "Khách sạn 5⭐ trung tâm Hà Nội",
                    "discount": "Giảm 15% cho khách SOVICO"
                }
            ],
            "hochiminhcity": [
                {
                    "id": "hotel_hcm_001",
                    "name": "Park Hyatt Saigon",
                    "type": "hotel", 
                    "rating": 5,
                    "price": 4500000,
                    "unit": "đêm",
                    "description": "Khách sạn sang trọng Q1",
                    "discount": "Upgrade phòng miễn phí"
                }
            ],
            "danang": [
                {
                    "id": "hotel_dn_001",
                    "name": "Sovico Beach Resort",
                    "type": "hotel",
                    "rating": 5,
                    "price": 3500000,
                    "unit": "đêm",
                    "description": "Resort 5⭐ view biển Đà Nẵng",
                    "discount": "Giảm 20% + spa miễn phí"
                }
            ]
        }
        
        # Tìm theo tên chuẩn hóa
        for key in hotel_data.keys():
            if key in dest_normalized or dest_normalized in key:
                return hotel_data[key]
        
        # Fallback: tạo hotel generic
        return [{
            "id": f"hotel_{dest_normalized}_001",
            "name": f"Sovico Hotel {destination}",
            "type": "hotel",
            "rating": 4,
            "price": 2000000,
            "unit": "đêm",
            "description": f"Khách sạn Sovico tại {destination}",
            "discount": "Giảm 15% cho khách SOVICO"
        }]
    
    def _get_airport_transfer(self, destination: str) -> Dict[str, Any]:
        """Xe đưa đón sân bay"""
        
        transfer_prices = {
            "Hanoi": 350000,
            "Ho Chi Minh City": 400000,
            "Da Nang": 300000
        }
        
        price = transfer_prices.get(destination, 350000)
        
        return {
            "id": f"transfer_{destination.lower().replace(' ', '_')}",
            "name": "Xe đưa đón sân bay SOVICO",
            "type": "transfer",
            "price": price,
            "unit": "chuyến",
            "description": f"Xe riêng đưa đón sân bay - {destination}",
            "features": ["Xe đời mới", "Tài xế chuyên nghiệp", "Đúng giờ", "Miễn phí nước uống"],
            "discount": "Giảm 10% khi đặt cùng vé máy bay"
        }
    
    def _get_destination_tours(self, destination: str) -> List[Dict[str, Any]]:
        """Tour du lịch tại điểm đến"""
        
        tour_data = {
            "Hanoi": [
                {
                    "id": "tour_hn_001",
                    "name": "Hà Nội City Tour 1 ngày",
                    "type": "tour",
                    "price": 850000,
                    "unit": "người",
                    "duration": "1 ngày",
                    "description": "Văn Miếu - Hồ Gươm - Phố Cổ - Chùa Một Cột",
                    "includes": ["Xe đưa đón", "Hướng dẫn viên", "Vé tham quan", "Ăn trưa"]
                },
                {
                    "id": "tour_hn_002",
                    "name": "Hạ Long Bay 2N1Đ",
                    "type": "tour",
                    "price": 2800000,
                    "unit": "người", 
                    "duration": "2 ngày 1 đêm",
                    "description": "Du thuyền Hạ Long - Hang Sửng Sốt - Đảo Titop",
                    "includes": ["Du thuyền 4⭐", "Ăn uống", "Hướng dẫn viên", "Kayak"]
                }
            ],
            "Ho Chi Minh City": [
                {
                    "id": "tour_hcm_001",
                    "name": "Sài Gòn City Tour",
                    "type": "tour",
                    "price": 750000,
                    "unit": "người",
                    "duration": "1 ngày",
                    "description": "Dinh Độc Lập - Chợ Bến Thành - Nhà Thờ Đức Bà",
                    "includes": ["Xe đưa đón", "Hướng dẫn viên", "Vé tham quan", "Ăn trưa"]
                },
                {
                    "id": "tour_hcm_002", 
                    "name": "Cần Thơ - Miệt Vườn 2N1Đ",
                    "type": "tour",
                    "price": 1950000,
                    "unit": "người",
                    "duration": "2 ngày 1 đêm",
                    "description": "Chợ nổi Cái Răng - Vườn trái cây - Làng nghề",
                    "includes": ["Khách sạn 3⭐", "Xe đưa đón", "Ăn uống", "Thuyền miệt vườn"]
                }
            ]
        }
        
        # Chuẩn hóa tên điểm đến
        dest_normalized = destination.lower().replace(' ', '')
        
        # Tìm theo tên chuẩn hóa
        for key in tour_data.keys():
            key_normalized = key.lower().replace(' ', '')
            if key_normalized in dest_normalized or dest_normalized in key_normalized:
                return tour_data[key]
        
        # Fallback: tạo tour generic
        return [{
            "id": f"tour_{dest_normalized}_001",
            "name": f"Tour {destination}",
            "type": "tour",
            "price": 800000,
            "unit": "người",
            "duration": "1 ngày",
            "description": f"Khám phá {destination}",
            "includes": ["Xe đưa đón", "Hướng dẫn viên"]
        }]
    
    def _get_travel_insurance(self) -> Dict[str, Any]:
        """Bảo hiểm du lịch"""
        
        return {
            "id": "insurance_travel_001",
            "name": "Bảo hiểm du lịch SOVICO Care",
            "type": "insurance",
            "price": 150000,
            "unit": "người/chuyến",
            "coverage": "5 tỷ VNĐ",
            "description": "Bảo hiểm toàn diện cho chuyến đi",
            "benefits": [
                "Tai nạn cá nhân: 5 tỷ VNĐ",
                "Chi phí y tế: 500 triệu VNĐ", 
                "Hủy chuyến: 50 triệu VNĐ",
                "Mất hành lý: 20 triệu VNĐ",
                "Hỗ trợ 24/7"
            ],
            "discount": "Miễn phí cho khách VIP (>5 booking)"
        }
    
    def _create_upsell_message(self, destination: str, service_type: str) -> str:
        """Tạo message gợi ý dịch vụ"""
        
        if service_type == "flight":
            return f"""
🎉 **CHÚC MỪNG ĐẶT VÉ THÀNH CÔNG!**

🌟 **DỊCH VỤ BỔ SUNG TẠI {destination.upper()}**

SOVICO có thể hỗ trợ thêm cho chuyến đi của bạn:

🏨 **Khách sạn** - Ưu đãi đặc biệt cho khách đặt vé
🚗 **Xe đưa đón** - Tiện lợi từ sân bay về trung tâm  
🎯 **Tour du lịch** - Khám phá điểm đến như người địa phương
🛡️ **Bảo hiểm** - An tâm cho chuyến đi

💝 **Ưu đãi đặc biệt:** Giảm 10-20% khi đặt combo với vé máy bay!

Bạn có muốn tìm hiểu thêm dịch vụ nào không?
""".strip()
        
        return "Bạn có cần thêm dịch vụ du lịch nào khác không?"
    
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
⭐ {service['rating']} sao
💰 {price:,} VNĐ/{service['unit']}
🎁 {service.get('discount', 'Không có ưu đãi')}

📝 Bạn muốn đặt từ ngày nào đến ngày nào?
👥 Số người: ? | Số phòng: ?
""".strip()
            
        elif service_type == "transfer":
            return f"""
🚗 **{name}**
💰 {price:,} VNĐ/{service['unit']}
🎁 {service.get('discount', 'Không có ưu đãi')}

✨ **Tính năng:**
{chr(10).join(f"• {feature}" for feature in service.get('features', []))}

📝 Bạn cần đưa đón lúc mấy giờ?
📍 Địa chỉ đón: ?
""".strip()
            
        elif service_type == "tour":
            return f"""
🎯 **{name}**
⏰ {service['duration']}
💰 {price:,} VNĐ/{service['unit']}

📋 **Bao gồm:**
{chr(10).join(f"• {item}" for item in service.get('includes', []))}

📅 Bạn muốn tham gia tour ngày nào?
👥 Số người tham gia: ?
""".strip()
            
        elif service_type == "insurance":
            return f"""
🛡️ **{name}**
💰 {price:,} VNĐ/{service['unit']}
🏥 Bảo hiểm: {service['coverage']}

🎯 **Quyền lợi:**
{chr(10).join(f"• {benefit}" for benefit in service.get('benefits', []))}

✅ Bạn có muốn mua bảo hiểm này không?
""".strip()
        
        return f"Chi tiết dịch vụ {name} - {price:,} VNĐ"

# Global instance
upsell_agent = UpsellAgent()