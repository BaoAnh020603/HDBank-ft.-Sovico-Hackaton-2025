import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class SemanticParser:
    """Parser ngữ nghĩa tổng quát cho các biểu thức mơ hồ"""
    
    def __init__(self):
        # Địa điểm
        self.location_mappings = {
            'sài gòn': 'Ho Chi Minh City', 'sg': 'Ho Chi Minh City', 'hcm': 'Ho Chi Minh City', 'tphcm': 'Ho Chi Minh City', 'tp hcm': 'Ho Chi Minh City', 'saigon': 'Ho Chi Minh City',
            'hà nội': 'Hanoi', 'hn': 'Hanoi', 'thủ đô': 'Hanoi', 'hanoi': 'Hanoi', 'ha noi': 'Hanoi',
            'đà nẵng': 'Da Nang', 'dn': 'Da Nang', 'da nang': 'Da Nang', 'danang': 'Da Nang',
            'nha trang': 'Nha Trang', 'nt': 'Nha Trang', 'nhatrang': 'Nha Trang',
            'phú quốc': 'Phu Quoc', 'pq': 'Phu Quoc', 'phu quoc': 'Phu Quoc', 'phuquoc': 'Phu Quoc', 'đảo ngọc': 'Phu Quoc',
            'đà lạt': 'Da Lat', 'dl': 'Da Lat', 'da lat': 'Da Lat', 'dalat': 'Da Lat', 'thành phố hoa': 'Da Lat',
            'cần thơ': 'Can Tho', 'ct': 'Can Tho', 'can tho': 'Can Tho', 'cantho': 'Can Tho', 'miền tây': 'Can Tho',
            'huế': 'Hue', 'hue': 'Hue', 'cố đô': 'Hue', 'kinh thành': 'Hue',
            'vũng tàu': 'Vung Tau', 'vt': 'Vung Tau', 'vung tau': 'Vung Tau', 'vungtau': 'Vung Tau', 'bà rịa': 'Vung Tau',
            'quy nhon': 'Quy Nhon', 'qn': 'Quy Nhon', 'quynhon': 'Quy Nhon', 'bình định': 'Quy Nhon',
            'hải phòng': 'Hai Phong', 'hp': 'Hai Phong', 'haiphong': 'Hai Phong', 'cảng': 'Hai Phong',
            'vinh': 'Vinh', 'nghệ an': 'Vinh', 'nghe an': 'Vinh',
            'pleiku': 'Pleiku', 'gia lai': 'Pleiku', 'gialai': 'Pleiku',
            'buôn ma thuột': 'Buon Ma Thuot', 'bmt': 'Buon Ma Thuot', 'đắk lắk': 'Buon Ma Thuot', 'daklak': 'Buon Ma Thuot',
            'côn đảo': 'Con Dao', 'con dao': 'Con Dao', 'condao': 'Con Dao',
            'rạch giá': 'Rach Gia', 'rach gia': 'Rach Gia', 'rachgia': 'Rach Gia', 'kiên giang': 'Rach Gia',
            'cà mau': 'Ca Mau', 'ca mau': 'Ca Mau', 'camau': 'Ca Mau', 'mũi cà mau': 'Ca Mau'
        }
        
        # Số lượng người
        self.passenger_keywords = {
            'một người': 1, '1 người': 1, 'mình': 1, 'tôi': 1, 'em': 1, 'anh': 1, 'chị': 1, 'cô': 1, 'chú': 1,
            'hai người': 2, '2 người': 2, 'vợ chồng': 2, 'cặp đôi': 2, 'hai vợ chồng': 2, 'hai đứa': 2, 'cả hai': 2, 'couple': 2,
            'ba người': 3, '3 người': 3, 'gia đình nhỏ': 3, 'ba đứa': 3, 'cả ba': 3, 'ba thành viên': 3,
            'bốn người': 4, '4 người': 4, 'gia đình': 4, 'bốn đứa': 4, 'cả bốn': 4, 'gia đình 4 người': 4,
            'năm người': 5, '5 người': 5, 'năm đứa': 5, 'cả năm': 5, 'gia đình lớn': 5,
            'sáu người': 6, '6 người': 6, 'nhóm nhỏ': 6, 'team nhỏ': 6,
            'bảy người': 7, '7 người': 7, 'nhóm': 7,
            'tám người': 8, '8 người': 8, 'đoàn nhỏ': 8,
            'chín người': 9, '9 người': 9, 'đoàn': 10, 'nhóm lớn': 10, 'team': 8, 'công ty': 15
        }
        
        # Loại chuyến bay
        self.trip_types = {
            'một chiều': 'one_way', 'khứ hồi': 'round_trip', 'round trip': 'round_trip',
            'đi về': 'round_trip', 'qua lại': 'round_trip', 'hai chiều': 'round_trip', 'tới lui': 'round_trip',
            'chỉ đi': 'one_way', 'không về': 'one_way', 'one way': 'one_way', 'đi thôi': 'one_way', 'đi không về': 'one_way',
            'vé khứ hồi': 'round_trip', 'vé đi về': 'round_trip', 'vé một chiều': 'one_way'
        }
        
        # Hạng ghế
        self.seat_classes = {
            'phổ thông': 'economy', 'eco': 'economy', 'thường': 'economy', 'economy': 'economy', 'bình thường': 'economy', 'rẻ': 'economy',
            'thương gia': 'business', 'business': 'business', 'vip': 'business', 'premium': 'business', 'sang': 'business', 'đẹp': 'business',
            'hạng nhất': 'first', 'first': 'first', 'cao cấp': 'first', 'luxury': 'first', 'sang trọng': 'first', 'đắt tiền': 'first', 'first class': 'first'
        }
        
        # Thời gian bay
        self.flight_times = {
            'sáng sớm': '06:00', 'sớm': '06:00', 'rất sớm': '05:00', 'dawn': '06:00',
            'sáng': '08:00', 'buổi sáng': '08:00', 'morning': '08:00', 'sáng muộn': '09:00',
            'trưa': '12:00', 'buổi trưa': '12:00', 'noon': '12:00', 'giữa trưa': '12:00',
            'chiều': '15:00', 'buổi chiều': '15:00', 'afternoon': '15:00', 'chiều sớm': '14:00', 'chiều muộn': '16:00',
            'tối': '18:00', 'buổi tối': '18:00', 'evening': '18:00', 'tối sớm': '17:00',
            'đêm': '21:00', 'buổi đêm': '21:00', 'night': '21:00', 'tối muộn': '20:00',
            'muộn': '22:00', 'rất muộn': '23:00', 'khuya': '23:00', 'late': '22:00', 'midnight': '00:00'
        }
        
        # Giá cả
        self.price_ranges = {
            'rẻ': {'max': 2000000, 'type': 'budget'}, 'rẻ nhất': {'max': 1500000, 'type': 'cheapest'}, 'giá rẻ': {'max': 2000000, 'type': 'budget'},
            'tiết kiệm': {'max': 1500000, 'type': 'budget'}, 'budget': {'max': 1800000, 'type': 'budget'}, 'tối ưu': {'max': 2200000, 'type': 'budget'},
            'bình thường': {'min': 2000000, 'max': 5000000, 'type': 'normal'}, 'trung bình': {'min': 2500000, 'max': 4500000, 'type': 'normal'},
            'ổn': {'min': 2000000, 'max': 4000000, 'type': 'normal'}, 'vừa phải': {'min': 2200000, 'max': 4200000, 'type': 'normal'},
            'đắt': {'min': 5000000, 'type': 'premium'}, 'cao': {'min': 4500000, 'type': 'premium'}, 'premium': {'min': 5500000, 'type': 'premium'},
            'cao cấp': {'min': 8000000, 'type': 'luxury'}, 'luxury': {'min': 10000000, 'type': 'luxury'}, 'sang trọng': {'min': 8500000, 'type': 'luxury'},
            'vip': {'min': 7000000, 'type': 'luxury'}, 'đắt tiền': {'min': 6000000, 'type': 'premium'}
        }
        
        # Hãng hàng không - Tập trung VietJet (Sovico ecosystem)
        self.airlines = {
            # VietJet - Ưu tiên chính
            'vietjet': 'VJ', 'vietjet air': 'VJ', 'vj': 'VJ', 'máy bay vàng': 'VJ',
            'viet jet': 'VJ', 'vietjetair': 'VJ', 'sovico': 'VJ', 'hãng vàng': 'VJ',
            'vietjet airways': 'VJ', 'new age': 'VJ', 'tân thời đại': 'VJ',
            'giá rẻ': 'VJ', 'low cost': 'VJ', 'lcc': 'VJ', 'budget airline': 'VJ',
            
            # Các hãng khác - Hỗ trợ
            'vietnam airlines': 'VN', 'vna': 'VN', 'vietnam airline': 'VN', 'hãng cờ': 'VN',
            'jetstar': 'BL', 'jetstar pacific': 'BL', 'bl': 'BL', 'sao xanh': 'BL',
            'bamboo airways': 'QH', 'bamboo': 'QH', 'qh': 'QH', 'tre việt': 'QH'
        }
        
        # Mục đích chuyến đi
        self.trip_purposes = {
            'du lịch': 'tourism', 'nghỉ dưỡng': 'vacation', 'vacation': 'vacation', 'holiday': 'vacation',
            'công việc': 'business', 'business': 'business', 'làm việc': 'business', 'họp': 'business',
            'thăm gia đình': 'family', 'về quê': 'family', 'thăm người thân': 'family', 'family': 'family',
            'khám chữa bệnh': 'medical', 'y tế': 'medical', 'medical': 'medical', 'bệnh viện': 'medical',
            'học tập': 'education', 'đi học': 'education', 'education': 'education', 'trường': 'education'
        }
        
        # Độ ưu tiên
        self.priorities = {
            'gấp': 'urgent', 'khẩn cấp': 'urgent', 'urgent': 'urgent', 'cấp bách': 'urgent',
            'bình thường': 'normal', 'normal': 'normal', 'không gấp': 'normal',
            'linh hoạt': 'flexible', 'flexible': 'flexible', 'tùy ý': 'flexible'
        }
        
        # Yêu cầu đặc biệt
        self.special_requests = {
            'suất ăn chay': 'vegetarian_meal', 'chay': 'vegetarian_meal', 'vegetarian': 'vegetarian_meal',
            'suất ăn halal': 'halal_meal', 'halal': 'halal_meal', 'muslim': 'halal_meal',
            'xe lăn': 'wheelchair', 'wheelchair': 'wheelchair', 'khuyết tật': 'wheelchair',
            'em bé': 'infant', 'trẻ em': 'child', 'infant': 'infant', 'baby': 'infant',
            'hành lý thêm': 'extra_baggage', 'baggage': 'extra_baggage', 'thêm hành lý': 'extra_baggage',
            'chỗ ngồi cửa sổ': 'window_seat', 'window': 'window_seat', 'cửa sổ': 'window_seat',
            'chỗ ngồi lối đi': 'aisle_seat', 'aisle': 'aisle_seat', 'lối đi': 'aisle_seat'
        }
    
    def parse_semantic_info(self, text: str) -> Dict[str, Any]:
        """Parse toàn bộ thông tin ngữ nghĩa từ text"""
        result = {}
        text_lower = text.lower()
        
        # Parse địa điểm
        locations = self._parse_locations(text_lower)
        if locations:
            result['locations'] = locations
        
        # Parse số lượng hành khách
        passengers = self._parse_passengers(text_lower)
        if passengers:
            result['passengers'] = passengers
        
        # Parse loại chuyến bay
        trip_type = self._parse_trip_type(text_lower)
        if trip_type:
            result['trip_type'] = trip_type
        
        # Parse hạng ghế
        seat_class = self._parse_seat_class(text_lower)
        if seat_class:
            result['seat_class'] = seat_class
        
        # Parse thời gian bay
        flight_time = self._parse_flight_time(text_lower)
        if flight_time:
            result['flight_time'] = flight_time
        
        # Parse giá cả
        price_range = self._parse_price_range(text_lower)
        if price_range:
            result['price_range'] = price_range
        
        # Parse thời gian (sử dụng time parser có sẵn)
        time_info = self._parse_time_expressions(text_lower)
        if time_info:
            result['time_info'] = time_info
        
        # Parse hãng hàng không
        airline = self._parse_airline(text_lower)
        if airline:
            result['airline'] = airline
        
        # Parse mục đích chuyến đi
        purpose = self._parse_trip_purpose(text_lower)
        if purpose:
            result['trip_purpose'] = purpose
        
        # Parse độ ưu tiên
        priority = self._parse_priority(text_lower)
        if priority:
            result['priority'] = priority
        
        # Parse yêu cầu đặc biệt
        special_requests = self._parse_special_requests(text_lower)
        if special_requests:
            result['special_requests'] = special_requests
        
        return result
    
    def _parse_locations(self, text: str) -> Optional[Dict[str, str]]:
        """Parse địa điểm đi và đến"""
        locations = {}
        
        # Tìm các từ khóa địa điểm
        found_locations = []
        for keyword, standard_name in self.location_mappings.items():
            if keyword in text:
                found_locations.append((keyword, standard_name))
        
        # Xác định điểm đi và điểm đến
        if len(found_locations) >= 2:
            # Tìm pattern "từ A đến B" hoặc "A - B"
            from_to_pattern = r'(từ|from)\s*([^đến]+)\s*(đến|to|->|-)\s*(.+)'
            match = re.search(from_to_pattern, text)
            
            if match:
                from_text = match.group(2).strip()
                to_text = match.group(4).strip()
                
                # Tìm địa điểm trong from_text và to_text
                for keyword, standard_name in self.location_mappings.items():
                    if keyword in from_text:
                        locations['from'] = standard_name
                    if keyword in to_text:
                        locations['to'] = standard_name
            else:
                # Nếu không có pattern rõ ràng, lấy 2 địa điểm đầu tiên
                locations['from'] = found_locations[0][1]
                locations['to'] = found_locations[1][1]
        
        elif len(found_locations) == 1:
            # Chỉ có 1 địa điểm, cần xác định là đi hay đến
            if any(word in text for word in ['đi', 'tới', 'đến', 'bay tới']):
                locations['to'] = found_locations[0][1]
            else:
                locations['from'] = found_locations[0][1]
        
        return locations if locations else None
    
    def _parse_passengers(self, text: str) -> Optional[int]:
        """Parse số lượng hành khách"""
        # Kiểm tra từ khóa cố định
        for keyword, count in self.passenger_keywords.items():
            if keyword in text:
                return count
        
        # Tìm pattern số + người
        number_pattern = r'(\d+)\s*người'
        match = re.search(number_pattern, text)
        if match:
            return int(match.group(1))
        
        return None
    
    def _parse_trip_type(self, text: str) -> Optional[str]:
        """Parse loại chuyến bay"""
        for keyword, trip_type in self.trip_types.items():
            if keyword in text:
                return trip_type
        return None
    
    def _parse_seat_class(self, text: str) -> Optional[str]:
        """Parse hạng ghế"""
        for keyword, seat_class in self.seat_classes.items():
            if keyword in text:
                return seat_class
        return None
    
    def _parse_flight_time(self, text: str) -> Optional[str]:
        """Parse thời gian bay trong ngày"""
        for keyword, time in self.flight_times.items():
            if keyword in text:
                return time
        return None
    
    def _parse_price_range(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse khoảng giá"""
        for keyword, price_info in self.price_ranges.items():
            if keyword in text:
                return price_info
        
        # Tìm pattern giá cụ thể
        price_patterns = [
            r'(\d+)\s*(triệu|tr)',  # 2 triệu
            r'(\d+)k',              # 500k
            r'(\d+)\s*đồng',        # 2000000 đồng
            r'dưới\s*(\d+)',        # dưới 2 triệu
            r'trên\s*(\d+)',        # trên 5 triệu
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                amount = int(match.group(1))
                
                if 'triệu' in pattern or 'tr' in pattern:
                    amount *= 1000000
                elif 'k' in pattern:
                    amount *= 1000
                
                if 'dưới' in text:
                    return {'max': amount, 'type': 'under'}
                elif 'trên' in text:
                    return {'min': amount, 'type': 'over'}
                else:
                    return {'target': amount, 'type': 'specific'}
        
        return None
    
    def _parse_airline(self, text: str) -> Optional[str]:
        """Parse hãng hàng không - Ưu tiên VietJet"""
        # Ưu tiên VietJet keywords trước
        vietjet_keywords = ['vietjet', 'vj', 'máy bay vàng', 'sovico', 'hãng vàng', 'giá rẻ', 'low cost']
        for keyword in vietjet_keywords:
            if keyword in text:
                return 'VJ'
        
        # Sau đó mới check các hãng khác
        for keyword, airline_code in self.airlines.items():
            if keyword in text and airline_code != 'VJ':
                return airline_code
        
        # Default về VietJet nếu không specify
        return 'VJ'
    
    def _parse_trip_purpose(self, text: str) -> Optional[str]:
        """Parse mục đích chuyến đi"""
        for keyword, purpose in self.trip_purposes.items():
            if keyword in text:
                return purpose
        return None
    
    def _parse_priority(self, text: str) -> Optional[str]:
        """Parse độ ưu tiên"""
        for keyword, priority in self.priorities.items():
            if keyword in text:
                return priority
        return None
    
    def _parse_special_requests(self, text: str) -> Optional[List[str]]:
        """Parse yêu cầu đặc biệt"""
        requests = []
        for keyword, request_type in self.special_requests.items():
            if keyword in text:
                requests.append(request_type)
        return requests if requests else None
    
    def _parse_time_expressions(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse biểu thức thời gian (tích hợp với time parser)"""
        from .time_parser import FlexibleTimeParser
        
        time_parser = FlexibleTimeParser()
        return time_parser.parse_time_expression(text)
    
    def extract_intent_details(self, text: str) -> Dict[str, Any]:
        """Trích xuất chi tiết ý định từ câu nói chung chung"""
        semantic_info = self.parse_semantic_info(text)
        
        # Xác định loại request
        intent_type = 'search'  # default
        
        if any(word in text.lower() for word in ['giá', 'bao nhiêu', 'cost', 'price']):
            intent_type = 'price_check'
        elif any(word in text.lower() for word in ['đặt', 'book', 'mua', 'order']):
            intent_type = 'booking'
        elif any(word in text.lower() for word in ['combo', 'gói', 'package']):
            intent_type = 'combo'
        
        return {
            'intent_type': intent_type,
            'semantic_info': semantic_info,
            'confidence': self._calculate_confidence(semantic_info),
            'missing_info': self._identify_missing_info(semantic_info, intent_type)
        }
    
    def _calculate_confidence(self, semantic_info: Dict[str, Any]) -> float:
        """Tính độ tin cậy dựa trên thông tin có được"""
        score = 0.0
        
        if semantic_info.get('locations'):
            score += 0.3  # Địa điểm quan trọng nhất
        if semantic_info.get('time_info'):
            score += 0.2  # Thời gian quan trọng thứ 2
        if semantic_info.get('passengers'):
            score += 0.15
        if semantic_info.get('trip_type'):
            score += 0.1
        if semantic_info.get('seat_class'):
            score += 0.1
        if semantic_info.get('flight_time'):
            score += 0.1
        if semantic_info.get('price_range'):
            score += 0.05
        
        return min(score, 1.0)
    
    def _identify_missing_info(self, semantic_info: Dict[str, Any], intent_type: str) -> List[str]:
        """Xác định thông tin còn thiếu"""
        missing = []
        
        # Thông tin bắt buộc cho mọi intent
        locations = semantic_info.get('locations', {})
        if not locations.get('from'):
            missing.append('departure_location')
        if not locations.get('to'):
            missing.append('arrival_location')
        if not semantic_info.get('time_info'):
            missing.append('departure_date')
        
        # Thông tin bắt buộc cho booking
        if intent_type == 'booking':
            if not semantic_info.get('passengers'):
                missing.append('passenger_count')
        
        return missing