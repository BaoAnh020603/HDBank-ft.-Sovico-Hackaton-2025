"""
SOVICO Services Data - Mock data thật về dịch vụ SOVICO
"""

from typing import Dict, List, Any

class SovicoDataProvider:
    """Provider cho mock data dịch vụ SOVICO"""
    
    @staticmethod
    def get_hotels(destination: str) -> List[Dict[str, Any]]:
        """Lấy danh sách khách sạn SOVICO theo điểm đến"""
        
        dest_normalized = destination.lower().replace(' ', '')
        
        hotel_data = {
            "hanoi": [
                {
                    "id": "sovico_hn_001",
                    "name": "Sovico Grand Hotel Hanoi",
                    "type": "hotel",
                    "rating": 5,
                    "price": 2200000,
                    "unit": "đêm",
                    "description": "Khách sạn 5⭐ trung tâm Hà Nội - Thương hiệu Sovico",
                    "discount": "Giảm 20% + miễn phí breakfast cho khách VietJet",
                    "amenities": ["Pool", "Spa", "Gym", "Business Center"],
                    "location": "Ba Đình, Hà Nội"
                },
                {
                    "id": "sovico_hn_002",
                    "name": "Sovico Boutique Hanoi",
                    "type": "hotel",
                    "rating": 4,
                    "price": 1500000,
                    "unit": "đêm",
                    "description": "Khách sạn boutique phong cách hiện đại",
                    "discount": "Giảm 15% cho khách đặt combo",
                    "amenities": ["Rooftop Bar", "Restaurant", "WiFi"],
                    "location": "Hoàn Kiếm, Hà Nội"
                }
            ],
            "hochiminhcity": [
                {
                    "id": "sovico_hcm_001",
                    "name": "Sovico Luxury Saigon",
                    "type": "hotel",
                    "rating": 5,
                    "price": 3800000,
                    "unit": "đêm",
                    "description": "Khách sạn sang trọng Q1 - View sông Sài Gòn",
                    "discount": "Upgrade suite miễn phí + Late checkout",
                    "amenities": ["Infinity Pool", "Sky Bar", "Spa", "Concierge"],
                    "location": "Quận 1, TP.HCM"
                },
                {
                    "id": "sovico_hcm_002",
                    "name": "Sovico Business Hotel",
                    "type": "hotel",
                    "rating": 4,
                    "price": 2200000,
                    "unit": "đêm",
                    "description": "Khách sạn doanh nhân trung tâm Q3",
                    "discount": "Miễn phí meeting room 2h",
                    "amenities": ["Business Center", "Meeting Rooms", "Gym"],
                    "location": "Quận 3, TP.HCM"
                }
            ],
            "danang": [
                {
                    "id": "sovico_dn_001",
                    "name": "Sovico Beach Resort Da Nang",
                    "type": "hotel",
                    "rating": 5,
                    "price": 4200000,
                    "unit": "đêm",
                    "description": "Resort 5⭐ view biển Mỹ Khê - All-inclusive",
                    "discount": "Giảm 25% + miễn phí spa + Kids club",
                    "amenities": ["Private Beach", "Water Sports", "Kids Club", "Multiple Restaurants"],
                    "location": "Bãi biển Mỹ Khê, Đà Nẵng"
                }
            ],
            "nhatrang": [
                {
                    "id": "sovico_nt_001",
                    "name": "Sovico Ocean Resort Nha Trang",
                    "type": "hotel",
                    "rating": 5,
                    "price": 3500000,
                    "unit": "đêm",
                    "description": "Resort biển 5⭐ view vịnh Nha Trang",
                    "discount": "Giảm 20% + miễn phí water sports",
                    "amenities": ["Beachfront", "Water Sports", "Spa", "Multiple Pools"],
                    "location": "Trần Phú, Nha Trang"
                }
            ],
            "phuquoc": [
                {
                    "id": "sovico_pq_001",
                    "name": "Sovico Paradise Resort Phu Quoc",
                    "type": "hotel",
                    "rating": 5,
                    "price": 5200000,
                    "unit": "đêm",
                    "description": "Resort đảo thiên đường - Luxury experience",
                    "discount": "Giảm 30% + miễn phí island hopping",
                    "amenities": ["Private Villas", "Island Tours", "Diving Center", "Fine Dining"],
                    "location": "Bãi Sao, Phú Quốc"
                }
            ]
        }
        
        # Tìm theo tên chuẩn hóa
        for key in hotel_data.keys():
            if key in dest_normalized or dest_normalized in key:
                return hotel_data[key]
        
        # Fallback
        return [{
            "id": f"sovico_{dest_normalized}_001",
            "name": f"Sovico Hotel {destination}",
            "type": "hotel",
            "rating": 4,
            "price": 2000000,
            "unit": "đêm",
            "description": f"Khách sạn Sovico tại {destination}",
            "discount": "Giảm 15% cho khách SOVICO"
        }]
    
    @staticmethod
    def get_transfer(destination: str) -> Dict[str, Any]:
        """Lấy dịch vụ transfer SOVICO"""
        
        dest_normalized = destination.lower().replace(' ', '')
        
        transfer_services = {
            "hanoi": {"price": 380000, "vehicles": ["Toyota Vios", "Toyota Innova", "Mercedes E-Class"], "airport_code": "NOI"},
            "hochiminhcity": {"price": 420000, "vehicles": ["Toyota Vios", "Toyota Innova", "Mercedes E-Class"], "airport_code": "SGN"},
            "danang": {"price": 320000, "vehicles": ["Toyota Vios", "Toyota Innova"], "airport_code": "DAD"},
            "nhatrang": {"price": 350000, "vehicles": ["Toyota Vios", "Toyota Innova"], "airport_code": "CXR"},
            "phuquoc": {"price": 280000, "vehicles": ["Toyota Vios", "Toyota Innova"], "airport_code": "PQC"}
        }
        
        service_info = None
        for key, info in transfer_services.items():
            if key in dest_normalized or dest_normalized in key:
                service_info = info
                break
        
        if not service_info:
            service_info = {"price": 350000, "vehicles": ["Toyota Vios"], "airport_code": "XXX"}
        
        return {
            "id": f"sovico_transfer_{dest_normalized}",
            "name": "SOVICO Airport Transfer",
            "type": "transfer",
            "price": service_info["price"],
            "unit": "chuyến",
            "description": f"Dịch vụ đưa đón sân bay {service_info['airport_code']} - {destination}",
            "features": [
                f"Xe {service_info['vehicles'][0]} hoặc tương đương",
                "Tài xế chuyên nghiệp, giỏi tiếng Anh",
                "Theo dõi chuyến bay real-time",
                "Miễn phí nước suối + khăn lạnh",
                "Hỗ trợ hành lý",
                "Bảo hiểm hành khách"
            ],
            "discount": "Giảm 15% khi đặt combo với vé VietJet + khách sạn",
            "vehicle_options": service_info["vehicles"]
        }
    
    @staticmethod
    def get_tours(destination: str) -> List[Dict[str, Any]]:
        """Lấy danh sách tour SOVICO"""
        
        tour_data = {
            "Hanoi": [
                {
                    "id": "sovico_tour_hn_001",
                    "name": "Hà Nội Heritage Tour",
                    "type": "tour",
                    "price": 890000,
                    "unit": "người",
                    "duration": "1 ngày (8h)",
                    "description": "Khám phá di sản văn hóa Hà Nội với hướng dẫn viên chuyên nghiệp",
                    "includes": ["Xe đưa đón khách sạn", "Hướng dẫn viên tiếng Việt/Anh", "Vé tham quan", "Bữa trưa truyền thống", "Nước suối"],
                    "highlights": ["Văn Miếu Quốc Tử Giám", "Hồ Hoàn Kiếm", "Phố Cổ Hà Nội", "Chùa Một Cột", "Lăng Bác"],
                    "group_size": "Tối đa 15 khách"
                }
            ],
            "Ho Chi Minh City": [
                {
                    "id": "sovico_tour_hcm_001",
                    "name": "Sài Gòn Discovery Tour",
                    "type": "tour",
                    "price": 780000,
                    "unit": "người",
                    "duration": "1 ngày (7h)",
                    "description": "Khám phá Sài Gòn từ lịch sử đến hiện đại",
                    "includes": ["Xe đưa đón", "Hướng dẫn viên", "Vé tham quan", "Bữa trưa đặc sản", "Cafe Sài Gòn"],
                    "highlights": ["Dinh Độc Lập", "Bưu điện TP.HCM", "Chợ Bến Thành", "Nhà Thờ Đức Bà", "Phố đi bộ Nguyễn Huệ"],
                    "group_size": "Tối đa 12 khách"
                }
            ],
            "Da Nang": [
                {
                    "id": "sovico_tour_dn_001",
                    "name": "Bà Nà Hills & Hội An Combo",
                    "type": "tour",
                    "price": 1200000,
                    "unit": "người",
                    "duration": "1 ngày (10h)",
                    "description": "Kết hợp Bà Nà Hills và phố cổ Hội An trong 1 ngày",
                    "includes": ["Vé cáp treo Bà Nà", "Bữa trưa buffet", "Xe đưa đón", "Hướng dẫn viên", "Vé tham quan Hội An"],
                    "highlights": ["Cầu Vàng (Golden Bridge)", "Chùa Linh Ứng", "Phố cổ Hội An", "Chùa Cầu Nhật Bản"],
                    "group_size": "Tối đa 18 khách"
                }
            ]
        }
        
        dest_normalized = destination.lower().replace(' ', '')
        
        for key in tour_data.keys():
            key_normalized = key.lower().replace(' ', '')
            if key_normalized in dest_normalized or dest_normalized in key_normalized:
                return tour_data[key]
        
        return [{
            "id": f"sovico_tour_{dest_normalized}_001",
            "name": f"Tour {destination}",
            "type": "tour",
            "price": 800000,
            "unit": "người",
            "duration": "1 ngày",
            "description": f"Khám phá {destination}",
            "includes": ["Xe đưa đón", "Hướng dẫn viên"]
        }]
    
    @staticmethod
    def get_insurance() -> Dict[str, Any]:
        """Lấy bảo hiểm du lịch SOVICO"""
        
        return {
            "id": "sovico_insurance_001",
            "name": "SOVICO Travel Care Premium",
            "type": "insurance",
            "price": 180000,
            "unit": "người/chuyến",
            "coverage": "10 tỷ VNĐ",
            "description": "Bảo hiểm du lịch toàn diện - Đối tác chiến lược với VietJet",
            "benefits": [
                "Tai nạn cá nhân: 10 tỷ VNĐ",
                "Chi phí y tế: 1 tỷ VNĐ",
                "Hủy/hoãn chuyến: 100 triệu VNĐ",
                "Mất/chậm hành lý: 50 triệu VNĐ",
                "Trợ cấp cứu 24/7 toàn cầu",
                "Bảo hiểm COVID-19",
                "Hỗ trợ pháp lý",
                "Bảo hiểm thể thao mạo hiểm"
            ],
            "discount": "Giảm 20% khi mua combo với vé VietJet + khách sạn SOVICO",
            "validity": "30 ngày kể từ ngày khởi hành",
            "coverage_area": "Toàn cầu (trừ các vùng xung đột)",
            "claim_hotline": "1900-SOVICO (24/7)"
        }