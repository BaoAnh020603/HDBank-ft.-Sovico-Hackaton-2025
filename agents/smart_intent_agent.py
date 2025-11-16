"""
Smart Intent Agent - Phát hiện ý định thông minh dựa trên context
"""

from typing import Dict, Any, List
import re

class SmartIntentAgent:
    """Agent phát hiện ý định thông minh với context awareness"""
    
    def __init__(self):
        self.name = "SmartIntentAgent"
        self.conversation_context = {}
    
    def analyze_intent(self, user_message: str, conversation_history: List[Dict] = None, user_id: str = None) -> Dict[str, Any]:
        """Phân tích ý định dựa trên message và context"""
        
        # Cập nhật context
        if user_id:
            if user_id not in self.conversation_context:
                self.conversation_context[user_id] = {
                    "last_search": None,
                    "selected_flight": None,
                    "booking_stage": None,
                    "messages": []
                }
            
            self.conversation_context[user_id]["messages"].append({
                "message": user_message,
                "timestamp": "now"
            })
        
        context = self.conversation_context.get(user_id, {})
        
        # Phân tích các loại intent
        search_intent = self._analyze_search_intent(user_message, context)
        booking_intent = self._analyze_booking_intent(user_message, context, conversation_history)
        info_intent = self._analyze_info_intent(user_message, context)
        
        # Debug output
        print(f"DEBUG Intent Analysis for '{user_message}': search={search_intent['confidence']:.2f}, booking={booking_intent['confidence']:.2f}, info={info_intent['confidence']:.2f}")
        print(f"DEBUG Context: has_search={bool(context.get('last_search'))}, user_id={user_id}")
        
        # Quyết định intent chính - ưu tiên booking intent cao hơn
        selected_intent = None
        if booking_intent["confidence"] > 0.8:
            selected_intent = booking_intent
        elif booking_intent["confidence"] > 0.6 and booking_intent["confidence"] > search_intent["confidence"]:
            selected_intent = booking_intent
        elif search_intent["confidence"] > 0.6:
            selected_intent = search_intent
        elif booking_intent["confidence"] > 0.5:
            selected_intent = booking_intent
        elif info_intent["confidence"] > 0.5:
            selected_intent = info_intent
        else:
            selected_intent = {"intent": "unknown", "confidence": 0.0}
        
        print(f"DEBUG Selected intent: {selected_intent['intent']} (confidence: {selected_intent.get('confidence', 0):.2f})")
        return selected_intent
    
    def _analyze_booking_intent(self, message: str, context: Dict, history: List = None) -> Dict[str, Any]:
        """Phân tích ý định đặt vé - THÔNG MINH hơn"""
        
        message_lower = message.lower().strip()
        confidence = 0.0
        
        # Kiểm tra context: có kết quả tìm kiếm gần đây không?
        has_recent_search = context.get("last_search") is not None
        
        # Patterns đặt vé MẠNH - exact matches first
        if message_lower == "đặt vé này":
            confidence = 0.95
        elif message_lower in ["đặt vé", "book vé", "mua vé này", "đặt chuyến này"]:
            confidence = 0.9
        elif message_lower in ["đặt vé cho tôi", "đặt cho tôi"]:
            confidence = 0.9
        # QUAN TRỌNG: Pattern cho "hãy đặt cho tôi chuyến bay đó"
        elif "hãy đặt" in message_lower and has_recent_search:
            confidence = 0.95
        elif "đặt cho tôi chuyến" in message_lower and has_recent_search:
            confidence = 0.9
        # Patterns yêu cầu vé rẻ nhất khi đã có kết quả tìm kiếm
        elif has_recent_search and any(phrase in message_lower for phrase in [
            "cho tôi vé", "vé rẻ nhất", "đưa cho tôi", "thông tin vé", "chọn vé",
            "chuyến bay đó", "chuyến đó", "vé đó"
        ]):
            confidence = 0.85
        else:
            # Patterns đặt vé MẠNH
            strong_booking_patterns = [
                r"đặt vé.*này",
                r"đặt.*chuyến.*này", 
                r"book.*này",
                r"mua vé.*này",
                r"chọn.*chuyến.*này"
            ]
            
            # Kiểm tra strong patterns
            for pattern in strong_booking_patterns:
                if re.search(pattern, message_lower):
                    confidence = 0.9
                    break
            
            # Thêm patterns đặc biệt cho context
            if confidence == 0.0 and has_recent_search:
                context_booking_patterns = [
                    r"hãy đặt.*cho.*tôi",
                    r"đặt.*cho.*tôi.*chuyến",
                    r"cho.*tôi.*chuyến.*đó",
                    r"đặt.*chuyến.*đó"
                ]
                
                for pattern in context_booking_patterns:
                    if re.search(pattern, message_lower):
                        confidence = 0.9
                        break
            
            # Kiểm tra medium patterns
            if confidence == 0.0:
                medium_booking_patterns = [
                    r"đặt vé",
                    r"tôi muốn đặt",
                    r"book vé",
                    r"mua vé",
                    r"cho tôi.*vé",
                    r"vé.*rẻ nhất",
                    r"thông tin.*vé.*rẻ"
                ]
                
                for pattern in medium_booking_patterns:
                    if re.search(pattern, message_lower):
                        if has_recent_search:
                            confidence = 0.8  # Có context nên cao hơn
                        else:
                            confidence = 0.6  # Cần xác nhận
                        break
        
        # Giảm confidence nếu chỉ là câu hỏi
        question_indicators = ["?", "bao nhiêu", "như thế nào", "có", "không"]
        if any(indicator in message_lower for indicator in question_indicators):
            confidence *= 0.3
        
        # Trích xuất flight info từ context thực tế
        extracted_info = {}
        if has_recent_search and context.get("last_search"):
            # Lấy từ context nếu có
            extracted_info = context["last_search"]
        else:
            # Không tạo data tĩnh, để trống để BookingIntentAgent tự xử lý
            extracted_info = {}
        
        result = {
            "intent": "book_flight",
            "confidence": confidence,
            "requires_flight_selection": not has_recent_search,
            "context_available": has_recent_search,
            "extracted_info": extracted_info
        }
        
        print(f"DEBUG booking_intent result: {result}")
        return result
    
    def _analyze_search_intent(self, message: str, context: Dict) -> Dict[str, Any]:
        """Phân tích ý định tìm kiếm"""
        
        message_lower = message.lower()
        confidence = 0.0
        
        # Patterns tìm kiếm
        search_patterns = [
            r"giá vé.*từ.*đến",
            r"tìm.*chuyến bay",
            r"có chuyến.*không",
            r"giá.*rẻ nhất",
            r"chuyến bay.*nào",
            r"vé.*bao nhiêu"
        ]
        
        # Kiểm tra patterns
        for pattern in search_patterns:
            if re.search(pattern, message_lower):
                confidence += 0.4
        
        # Kiểm tra từ khóa địa điểm
        locations = ["hcm", "hà nội", "đà nẵng", "sài gòn", "hanoi", "ho chi minh", "từ", "đến"]
        location_count = sum(1 for loc in locations if loc in message_lower)
        if location_count >= 2:
            confidence += 0.5
        elif "giá vé" in message_lower or "vé" in message_lower:
            confidence += 0.3
        
        # Kiểm tra từ khóa thời gian
        time_keywords = ["hôm nay", "ngày mai", "tuần sau", "tháng"]
        if any(keyword in message_lower for keyword in time_keywords):
            confidence += 0.2
        
        return {
            "intent": "search_flight",
            "confidence": min(confidence, 1.0),
            "extracted_info": self._extract_search_info(message)
        }
    
    def _analyze_info_intent(self, message: str, context: Dict) -> Dict[str, Any]:
        """Phân tích ý định hỏi thông tin và dịch vụ khác"""
        
        message_lower = message.lower()
        confidence = 0.0
        intent_type = "get_info"
        
        # Patterns thông tin chuyến bay
        flight_info_patterns = [
            r"thông tin.*chuyến bay",
            r"chi tiết.*vé",
            r"hành lý.*bao nhiêu",
            r"check.*in",
            r"hủy.*vé",
            r"đổi.*vé"
        ]
        
        # Patterns dịch vụ khác
        service_patterns = {
            "hotel": [r"khách sạn", r"phòng", r"hotel", r"lưu trú"],
            "transfer": [r"xe đưa đón", r"taxi", r"grab", r"transfer"],
            "tour": [r"tour", r"du lịch", r"tham quan", r"khám phá"],
            "insurance": [r"bảo hiểm", r"insurance"]
        }
        
        # Kiểm tra service patterns trước
        for service_type, patterns in service_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    confidence = 0.9
                    intent_type = f"request_{service_type}"
                    break
            if confidence > 0:
                break
        
        # Nếu không phải service, kiểm tra flight info
        if confidence == 0:
            for pattern in flight_info_patterns:
                if re.search(pattern, message_lower):
                    confidence = 0.8
                    break
        
        # Kiểm tra "tìm cho tôi" trong context upselling
        if confidence == 0 and "tìm" in message_lower:
            # Kiểm tra context có upselling không
            recent_messages = context.get("messages", [])[-3:]
            recent_text = " ".join([msg.get("message", "") for msg in recent_messages]).lower()
            
            if any(service in recent_text for service in ["khách sạn", "xe đưa", "tour", "dịch vụ"]):
                confidence = 0.8
                intent_type = "request_hotel"  # Default to hotel
        
        return {
            "intent": intent_type,
            "confidence": confidence
        }
    
    def _extract_search_info(self, message: str) -> Dict[str, Any]:
        """Trích xuất thông tin tìm kiếm"""
        
        message_lower = message.lower()
        
        # Trích xuất địa điểm
        location_map = {
            "hcm": "Ho Chi Minh City",
            "sài gòn": "Ho Chi Minh City", 
            "tp.hcm": "Ho Chi Minh City",
            "hà nội": "Hanoi",
            "hn": "Hanoi",
            "đà nẵng": "Da Nang",
            "dn": "Da Nang"
        }
        
        from_city = None
        to_city = None
        
        # Tìm pattern "từ X đến Y"
        from_to_pattern = r"từ\s+([^đến]+)\s+đến\s+([^\s]+)"
        match = re.search(from_to_pattern, message_lower)
        
        if match:
            from_text = match.group(1).strip()
            to_text = match.group(2).strip()
            
            for key, value in location_map.items():
                if key in from_text:
                    from_city = value
                if key in to_text:
                    to_city = value
        
        # Trích xuất thời gian
        date = None
        if "hôm nay" in message_lower:
            date = "hôm nay"
        elif "ngày mai" in message_lower:
            date = "ngày mai"
        
        return {
            "from_city": from_city,
            "to_city": to_city,
            "date": date
        }
    
    def update_context(self, user_id: str, key: str, value: Any):
        """Cập nhật context"""
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = {
                "last_search": None,
                "selected_flight": None,
                "booking_stage": None,
                "messages": []
            }
        
        self.conversation_context[user_id][key] = value
    
    def get_context(self, user_id: str) -> Dict[str, Any]:
        """Lấy context"""
        return self.conversation_context.get(user_id, {})
    
    def should_proceed_with_booking(self, user_message: str, user_id: str) -> Dict[str, Any]:
        """Quyết định có nên tiến hành đặt vé không"""
        
        intent_result = self.analyze_intent(user_message, user_id=user_id)
        
        # Debug output
        print(f"DEBUG SmartIntent should_proceed_with_booking: Message='{user_message}', Intent={intent_result['intent']}, Confidence={intent_result.get('confidence', 0):.2f}")
        print(f"DEBUG SmartIntent context: {self.get_context(user_id)}")
        
        if intent_result["intent"] == "book_flight" and intent_result["confidence"] > 0:
            context = self.get_context(user_id)
            
            # Nếu có confidence cao
            if intent_result["confidence"] >= 0.8:
                print(f"DEBUG: High confidence booking intent - proceeding")
                return {
                    "should_book": True,
                    "confidence": intent_result["confidence"],
                    "reason": "Strong booking intent detected"
                }
            
            # Nếu confidence trung bình - hỏi xác nhận
            elif intent_result["confidence"] >= 0.5:
                print(f"DEBUG: Medium confidence booking intent - asking confirmation")
                return {
                    "should_book": False,
                    "should_confirm": True,
                    "confidence": intent_result["confidence"],
                    "reason": "Ambiguous intent - need confirmation"
                }
            
            # Nếu confidence thấp nhưng có context
            elif intent_result["confidence"] > 0 and context.get("last_search"):
                print(f"DEBUG: Low confidence but has context - asking confirmation")
                return {
                    "should_book": False,
                    "should_confirm": True,
                    "confidence": intent_result["confidence"],
                    "reason": "Low confidence but has context - need confirmation"
                }
            
            # Nếu confidence thấp và không có context
            else:
                print(f"DEBUG: Low confidence and no context - not booking")
                return {
                    "should_book": False,
                    "should_confirm": False,
                    "confidence": intent_result["confidence"],
                    "reason": "Low confidence - not booking intent"
                }
        
        print(f"DEBUG: No booking intent detected")
        return {
            "should_book": False,
            "should_confirm": False,
            "confidence": intent_result.get("confidence", 0.0),
            "reason": "No booking intent detected"
        }

# Global instance
smart_intent_agent = SmartIntentAgent()