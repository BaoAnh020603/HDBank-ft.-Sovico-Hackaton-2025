import re
from typing import Dict, Tuple, Any
from datetime import datetime, timedelta
from difflib import SequenceMatcher
try:
    from underthesea import word_tokenize
    from fuzzywuzzy import fuzz, process
except ImportError:
    word_tokenize = None
    fuzz = None
    process = None

class VietnameseNLU:
    """Vietnamese NLU engine for intent detection and slot extraction"""
    
    def __init__(self):
        # Intent patterns với nhiều biến thể tiếng Việt
        self.intent_patterns = {
            "flight_search": [
                r"tìm.*chuyến bay", r"có.*vé.*máy bay", r"chuyến bay.*nào", r"vé.*từ.*đến", 
                r"bay.*từ.*đến", r"còn.*vé.*không", r"xem.*chuyến bay", r"kiểm tra.*vé",
                r"tìm.*vé", r"search.*flight", r"flight.*available", r"vé.*còn.*không",
                r"có.*chuyến.*nào", r"chuyến.*bay.*gì", r"máy bay.*từ", r"đi.*máy bay"
            ],
            "price_check": [
                r"giá.*vé", r"bao nhiêu.*tiền", r"vé.*rẻ.*nhất", r"giá.*rẻ", r"chi phí", 
                r"price", r"cost", r"giá.*cả", r"tiền.*vé", r"vé.*giá", r"rẻ.*nhất",
                r"giá.*thế.*nào", r"hết.*bao nhiêu", r"tốn.*bao nhiêu", r"giá.*bán",
                r"vé.*rẻ.*nhất.*bao nhiêu", r"giá.*rẻ.*nhất"
            ],
            "booking": [
                r"đặt.*vé", r"book.*vé", r"mua.*vé", r"đặt.*cho.*tôi", r"booking",
                r"order", r"purchase", r"buy", r"đặt.*chỗ", r"reserve", r"đặt.*ngay",
                r"mua.*ngay", r"chốt.*vé", r"lấy.*vé", r"đặt.*luôn", r"ok.*đặt",
                r"đặt.*rẻ.*nhất", r"đặt.*chuyến", r"đặt.*VN\d+", r"đặt.*VJ\d+",
                r"đặt.*BL\d+", r"đặt.*QH\d+"
            ],
            "combo_service": [
                r"combo", r"gói.*dịch vụ", r"khách sạn.*thêm", r"xe.*đưa.*đón", 
                r"package", r"gói.*tour", r"dịch vụ.*thêm", r"combo.*gì", r"gói.*nào",
                r"thêm.*khách sạn", r"book.*thêm", r"có.*gì.*thêm", r"dịch vụ.*kèm",
                r"có.*combo", r"combo.*nào", r"combo.*không"
            ],
            "general": [
                r"xin chào", r"hello", r"hi", r"chào", r"hỗ trợ", r"giúp.*đỡ",
                r"cần.*giúp", r"hướng dẫn", r"trợ giúp", r"hỗ trợ.*gì"
            ]
        }
        
        # Mở rộng location mapping với nhiều cách gọi
        self.location_mapping = {
            # Hà Nội
            "hà nội": "HAN", "hanoi": "HAN", "hn": "HAN", "ha noi": "HAN",
            "thủ đô": "HAN", "nội bài": "HAN", "hà nội city": "HAN", "han": "HAN",
            
            # Đà Nẵng  
            "đà nẵng": "DAD", "da nang": "DAD", "đn": "DAD", "danang": "DAD",
            "da nẵng": "DAD", "đà nang": "DAD", "miền trung": "DAD", "dn": "DAD", "dad": "DAD",
            
            # TP.HCM
            "hồ chí minh": "SGN", "sài gòn": "SGN", "hcm": "SGN", "sgn": "SGN",
            "tp hcm": "SGN", "tp.hcm": "SGN", "saigon": "SGN", "tân sơn nhất": "SGN",
            "thành phố hồ chí minh": "SGN", "miền nam": "SGN"
        }
        
        # Mở rộng time patterns
        self.time_patterns = {
            "hôm nay": 0, "today": 0, "bây giờ": 0,
            "ngày mai": 1, "tomorrow": 1, "mai": 1,
            "ngày kia": 2, "một": 2,
            "tuần sau": 7, "next week": 7,
            "cuối tuần": 5, "weekend": 5, "thứ 7": 5, "chủ nhật": 6,
            "thứ hai": 1, "thứ ba": 2, "thứ tư": 3, "thứ năm": 4, "thứ sáu": 5
        }

    def extract_intent(self, message: str) -> str:
        """Extract intent linh hoạt với semantic understanding"""
        message_lower = self._normalize_vietnamese(message.lower())
        
        # Nếu câu hỏi quá ngắn hoặc chỉ chào hỏi
        if len(message_lower.strip()) < 3 or message_lower.strip() in ['hi', 'hello', 'chào']:
            return "general"
        
        # Semantic analysis thay vì chỉ pattern matching
        intent_scores = self._calculate_semantic_scores(message_lower)
        
        # Tìm intent có điểm cao nhất
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            best_score = intent_scores[best_intent]
            
            # Nếu không có intent nào rõ ràng (score < 0.3)
            if best_score < 0.3:
                return self._handle_ambiguous_intent(message_lower)
            
            return best_intent
        
        return "general"
    
    def _calculate_semantic_scores(self, message: str) -> Dict[str, float]:
        """Tính điểm semantic cho từng intent với logic cải tiến"""
        scores = {}
        
        # Định nghĩa semantic keywords với trọng số
        semantic_keywords = {
            'flight_search': {
                'strong': ['tìm vé', 'chuyến bay', 'máy bay', 'tìm chuyến'],
                'medium': ['tìm', 'vé', 'bay', 'chuyến', 'còn vé', 'có vé'],
                'weak': ['từ', 'đến', 'đi', 'khởi hành']
            },
            'price_check': {
                'strong': ['giá vé', 'bao nhiêu tiền', 'vé rẻ nhất', 'chi phí'],
                'medium': ['giá', 'tiền', 'bao nhiêu', 'rẻ', 'đắt', 'cost'],
                'weak': ['nhất', 'cả', 'thế nào']
            },
            'booking': {
                'strong': ['đặt vé', 'book vé', 'mua vé', 'đặt chỗ'],
                'medium': ['đặt', 'book', 'mua', 'order', 'chốt'],
                'weak': ['ngay', 'luôn', 'cho tôi']
            },
            'combo_service': {
                'strong': ['combo', 'gói dịch vụ', 'khách sạn'],
                'medium': ['gói', 'tour', 'dịch vụ thêm'],
                'weak': ['thêm', 'kèm', 'package']
            },
            'general': {
                'strong': ['xin chào', 'hello', 'hi', 'cảm ơn', 'thanks'],
                'medium': ['chào', 'hỗ trợ', 'giúp', 'hướng dẫn', 'làm sao', 'như thế nào'],
                'weak': ['cần', 'muốn', 'có thể', 'được không']
            }
        }
        
        # Tính điểm cho từng intent
        for intent, keywords in semantic_keywords.items():
            score = 0.0
            
            # Strong keywords (3 điểm)
            for keyword in keywords['strong']:
                if keyword in message:
                    score += 3.0
            
            # Medium keywords (1 điểm)
            for keyword in keywords['medium']:
                if keyword in message:
                    score += 1.0
            
            # Weak keywords (0.3 điểm)
            for keyword in keywords['weak']:
                if keyword in message:
                    score += 0.3
            
            scores[intent] = score
        
        return scores
    
    def _handle_ambiguous_intent(self, message: str) -> str:
        """Xử lý intent không rõ ràng với logic thông minh hơn"""
        message_lower = message.lower()
        
        # Ưu tiên general cho các câu hỏi chung
        general_indicators = [
            'làm sao', 'như thế nào', 'có thể', 'được không', 'gì', 'nào',
            'dịch vụ', 'hỗ trợ', 'giúp', 'tư vấn', 'hướng dẫn',
            'an toàn', 'tin tưởng', 'bảo mật', 'uy tín'
        ]
        
        if any(indicator in message_lower for indicator in general_indicators):
            return 'general'
        
        # Kiểm tra flight-related nhưng không cụ thể
        flight_words = ['vé', 'bay', 'chuyến', 'máy bay']
        has_flight_context = any(word in message_lower for word in flight_words)
        
        if has_flight_context:
            # Nếu có từ khóa đặt/mua -> booking
            if any(word in message_lower for word in ['đặt', 'mua', 'book']):
                return 'booking'
            # Nếu có từ khóa giá -> price_check
            elif any(word in message_lower for word in ['giá', 'tiền', 'bao nhiêu']):
                return 'price_check'
            # Còn lại -> flight_search
            else:
                return 'flight_search'
        
        # Nếu chỉ hỏi về giá mà không có context flight
        if any(word in message_lower for word in ['giá', 'tiền', 'bao nhiêu']):
            return 'price_check'
        
        # Default: general
        return 'general'
    
    def _similarity(self, a: str, b: str) -> float:
        """Tính độ tương đồng giữa 2 string"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def _normalize_vietnamese(self, text: str) -> str:
        """Chuẩn hóa text tiếng Việt"""
        # Loại bỏ dấu câu thừa
        text = re.sub(r'[^\w\s]', ' ', text)
        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_slots(self, message: str) -> Dict[str, Any]:
        """Extract slots from message với xử lý tiếng Việt nâng cao"""
        slots = {}
        message_lower = self._normalize_vietnamese(message.lower())
        
        # Extract locations với fuzzy matching và mã ngắn
        locations = []
        location_matches = []
        
        for location, code in self.location_mapping.items():
            # Kiểm tra cả tên đầy đủ và mã ngắn
            if location in message_lower or code.lower() in message_lower:
                locations.append(code)
                location_matches.append((location, code))
            # Fuzzy matching cho địa danh
            elif process and len(location) > 3:
                match = process.extractOne(location, [message_lower], scorer=fuzz.partial_ratio)
                if match and match[1] > 80:  # 80% similarity
                    locations.append(code)
                    location_matches.append((location, code))
        
        # FIX: Xử lý các pattern từ...đến, từ...tới, bay từ...đến
        patterns_to_check = [
            ("đi", "đi"),  # "HN đi DN"
            ("từ", "đến"),  # "từ HCM đến HN"
            ("từ", "tới"),  # "từ HCM tới HN"
            ("bay từ", "đến"),  # "bay từ HCM đến HN"
            ("bay từ", "tới")   # "bay từ HCM tới HN"
        ]
        
        for from_keyword, to_keyword in patterns_to_check:
            if from_keyword in message_lower and to_keyword in message_lower:
                # Tìm vị trí của keywords
                from_pos = message_lower.find(from_keyword)
                to_pos = message_lower.find(to_keyword)
                
                if from_pos != -1 and to_pos != -1 and from_pos < to_pos:
                    # Extract phần giữa from_keyword và to_keyword
                    from_part = message_lower[from_pos + len(from_keyword):to_pos].strip()
                    # Extract phần sau to_keyword
                    to_part = message_lower[to_pos + len(to_keyword):].strip()
                    
                    # Tìm location trong from_part
                    for location, code in self.location_mapping.items():
                        if location in from_part or code.lower() in from_part:
                            slots["from_city"] = code
                            break
                    
                    # Tìm location trong to_part
                    for location, code in self.location_mapping.items():
                        if location in to_part or code.lower() in to_part:
                            slots["to_city"] = code
                            break
                    
                    # Nếu đã tìm thấy cả 2, thoát khỏi loop
                    if slots.get("from_city") and slots.get("to_city"):
                        break
        
        # Nếu chưa có location nào từ pattern "đi", thử extract thông thường
        if not slots.get("from_city") and not slots.get("to_city") and len(locations) >= 2:
            # Tìm vị trí của "từ" và "đến" để xác định thứ tự
            from_keywords = ["từ", "from", "khởi hành"]
            to_keywords = ["đến", "to", "tới", "về"]
            
            from_pos = -1
            to_pos = -1
            
            for keyword in from_keywords:
                pos = message_lower.find(keyword)
                if pos != -1:
                    from_pos = pos
                    break
            
            for keyword in to_keywords:
                pos = message_lower.find(keyword)
                if pos != -1:
                    to_pos = pos
                    break
            
            if from_pos != -1 and to_pos != -1 and from_pos < to_pos:
                # Tìm location gần "từ" và "đến" nhất
                from_location = None
                to_location = None
                
                for loc_text, code in location_matches:
                    loc_pos = message_lower.find(loc_text)
                    if loc_pos != -1:
                        if loc_pos > from_pos and (from_location is None or loc_pos < message_lower.find(from_location[0])):
                            from_location = (loc_text, code)
                        if loc_pos > to_pos and (to_location is None or loc_pos < message_lower.find(to_location[0])):
                            to_location = (loc_text, code)
                
                if from_location:
                    slots["from_city"] = from_location[1]
                if to_location:
                    slots["to_city"] = to_location[1]
            else:
                # Fallback: thứ tự xuất hiện
                slots["from_city"] = locations[0]
                slots["to_city"] = locations[1]
        elif not slots.get("from_city") and not slots.get("to_city") and len(locations) == 1:
            slots["to_city"] = locations[0]
        
        # Extract dates với nhiều format
        self._extract_dates(message_lower, slots)
        
        # FIX: Extract flight reference từ "vé đó", "chuyến này"
        if any(ref in message_lower for ref in ["vé đó", "chuyến này", "chuyến đó", "vé này"]):
            slots["flight_reference"] = True
        
        # Extract time ranges
        self._extract_time(message_lower, slots)
        
        # Extract class với nhiều cách gọi
        self._extract_class(message_lower, slots)
        
        # Extract service ID nếu có
        service_match = re.search(r"(VN|VJ|BL|QH)(\d+)", message_lower.upper())
        if service_match:
            flight_code = service_match.group(0)
            slots["flight_id"] = flight_code
        
        # FIX: Extract selection criteria từ "rẻ nhất", "đặt vé rẻ nhất"
        if "rẻ nhất" in message_lower or "cheapest" in message_lower:
            slots["selection_criteria"] = "cheapest"
            
        return slots
    
    def _extract_dates(self, message: str, slots: Dict[str, Any]):
        """Extract dates từ message"""
        # Time patterns
        for time_phrase, days_offset in self.time_patterns.items():
            if time_phrase in message:
                if isinstance(days_offset, int):
                    target_date = datetime.now() + timedelta(days=days_offset)
                else:
                    # Xử lý thứ trong tuần
                    today = datetime.now()
                    days_ahead = days_offset - today.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    target_date = today + timedelta(days=days_ahead)
                slots["date"] = target_date.strftime("%Y-%m-%d")
                break
        
        # Specific date patterns (dd/mm, dd-mm, dd/mm/yyyy)
        date_patterns = [
            r"(\d{1,2})/(\d{1,2})/(\d{4})",  # dd/mm/yyyy
            r"(\d{1,2})-(\d{1,2})-(\d{4})",  # dd-mm-yyyy
            r"(\d{1,2})/(\d{1,2})",         # dd/mm
            r"(\d{1,2})-(\d{1,2})"          # dd-mm
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3)) if len(match.groups()) > 2 else datetime.now().year
                
                try:
                    target_date = datetime(year, month, day)
                    slots["date"] = target_date.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
    
    def _extract_time(self, message: str, slots: Dict[str, Any]):
        """Extract time từ message"""
        # Time patterns
        time_patterns = [
            r"(\d{1,2}):(\d{2})",           # HH:MM
            r"(\d{1,2})h(\d{2})",           # HHhMM
            r"(\d{1,2})\s*giờ\s*(\d{2})",   # HH giờ MM
            r"(\d{1,2})h",                  # HHh
            r"(\d{1,2})\s*giờ"              # HH giờ
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
                
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    slots["time"] = f"{hour:02d}:{minute:02d}"
                    break
        
        # Time range keywords
        time_ranges = {
            "sáng": "06:00-11:59", "morning": "06:00-11:59",
            "trưa": "12:00-13:59", "noon": "12:00-13:59", 
            "chiều": "14:00-17:59", "afternoon": "14:00-17:59",
            "tối": "18:00-21:59", "evening": "18:00-21:59",
            "đêm": "22:00-05:59", "night": "22:00-05:59"
        }
        
        for keyword, time_range in time_ranges.items():
            if keyword in message:
                slots["time_range"] = time_range
                break
    
    def _extract_class(self, message: str, slots: Dict[str, Any]):
        """Extract class từ message"""
        business_keywords = ["business", "thương gia", "hạng thương gia", "business class"]
        economy_keywords = ["economy", "phổ thông", "hạng phổ thông", "economy class", "eco"]
        
        if any(keyword in message for keyword in business_keywords):
            slots["class_type"] = "Business"
        elif any(keyword in message for keyword in economy_keywords):
            slots["class_type"] = "Economy"

    def process(self, message: str, context: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        """Process message với khả năng trả lời linh hoạt mọi câu hỏi"""
        intent = self.extract_intent(message)
        slots = self.extract_slots(message)
        
        # Smart intent refinement
        intent = self._refine_intent_with_context(message, intent, context)
        
        # Merge with context if available
        if context:
            for key, value in context.items():
                if key not in slots and value and key != "last_search_results":
                    slots[key] = value
        
        # Thêm thông tin để hỗ trợ trả lời linh hoạt
        slots['original_message'] = message
        slots['message_length'] = len(message.split())
        slots['is_question'] = self._is_question(message)
        
        return intent, slots
    
    def _refine_intent_with_context(self, message: str, intent: str, context: Dict[str, Any]) -> str:
        """Tinh chỉnh intent dựa trên context và message"""
        message_lower = message.lower()
        
        # Xử lý "rẻ nhất" patterns
        if "rẻ nhất" in message_lower:
            if "đặt" in message_lower or "book" in message_lower or "mua" in message_lower:
                return "booking"
            elif "giá" in message_lower or "bao nhiêu" in message_lower:
                return "price_check"
        
        # Context-aware refinement
        if context and "intent" in context:
            previous_intent = context["intent"]
            
            # Câu hỏi ngắn dựa vào context
            if intent == "general" and len(message.split()) <= 4:
                if previous_intent == "flight_search":
                    if any(word in message_lower for word in ["giá", "bao nhiêu", "rẻ", "đắt"]):
                        return "price_check"
                    elif any(word in message_lower for word in ["đặt", "book", "ok", "được", "chốt"]):
                        return "booking"
                    elif any(word in message_lower for word in ["combo", "gói", "thêm"]):
                        return "combo_service"
                
                elif previous_intent == "price_check":
                    if any(word in message_lower for word in ["đặt", "book", "ok", "được", "mua"]):
                        return "booking"
        
        return intent
    
    def _is_question(self, message: str) -> bool:
        """Kiểm tra xem message có phải câu hỏi không"""
        question_indicators = [
            '?', 'không', 'gì', 'nào', 'như thế nào', 'làm sao', 'bao nhiêu',
            'có', 'được', 'what', 'how', 'when', 'where', 'why', 'which'
        ]
        return any(indicator in message.lower() for indicator in question_indicators)

    def can_handle_general_question(self, message: str) -> bool:
        """Kiểm tra xem có thể trả lời câu hỏi general không"""
        return True
    
    def should_handle_as_general(self, message: str, intent: str, confidence: float) -> bool:
        """Kiểm tra xem có nên xử lý như general question không"""
        # Nếu confidence thấp và có dấu hiệu general
        if confidence < 0.5:
            general_patterns = [
                'làm sao', 'như thế nào', 'có thể', 'được không',
                'dịch vụ gì', 'có gì', 'hỗ trợ', 'giúp đỡ', 'tư vấn',
                'an toàn', 'tin cậy', 'bảo mật', 'uy tín'
            ]
            return any(pattern in message.lower() for pattern in general_patterns)
        return False
    
    def get_response_context(self, message: str, intent: str) -> Dict[str, Any]:
        """Lấy context để tạo response phù hợp"""
        return {
            'message_type': 'question' if self._is_question(message) else 'statement',
            'politeness_level': self._detect_politeness(message),
            'urgency': self._detect_urgency(message),
            'topic_keywords': self._extract_topic_keywords(message)
        }
    
    def _detect_politeness(self, message: str) -> str:
        """Phát hiện mức độ lịch sự"""
        polite_words = ['xin', 'làm ơn', 'cảm ơn', 'please', 'thank', 'anh', 'chị', 'em']
        if any(word in message.lower() for word in polite_words):
            return 'polite'
        return 'neutral'
    
    def _detect_urgency(self, message: str) -> str:
        """Phát hiện mức độ khẩn cấp"""
        urgent_words = ['gấp', 'nhanh', 'urgent', 'asap', 'ngay', 'luôn', 'immediately']
        if any(word in message.lower() for word in urgent_words):
            return 'urgent'
        return 'normal'
    
    def _extract_topic_keywords(self, message: str) -> list:
        """Trích xuất từ khóa chủ đề"""
        # Loại bỏ stop words và lấy từ khóa quan trọng
        stop_words = {'là', 'của', 'và', 'có', 'được', 'này', 'đó', 'the', 'a', 'an', 'and', 'or'}
        words = [word for word in message.lower().split() if word not in stop_words and len(word) > 2]
        return words[:5]  # Lấy tối đa 5 từ khóa

# Alias để backward compatibility
SimpleNLU = VietnameseNLU