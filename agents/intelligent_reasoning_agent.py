from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.schema import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception as e:
    print(f"Warning: ChatGoogleGenerativeAI import failed in IntelligentReasoningAgent: {e}")
    ChatGoogleGenerativeAI = None
import json
import os

try:
    from agents.price_agent import PriceAgent
except ImportError:
    PriceAgent = None

class IntelligentReasoningAgent:
    """Multi-step reasoning agent with session context and specialized agent routing"""
    
    def __init__(self):
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        if ChatGoogleGenerativeAI and os.getenv("GOOGLE_API_KEY"):
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=0.1,
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            except Exception as e:
                print(f"Warning: Failed to initialize ChatGoogleGenerativeAI: {e}")
                self.llm = None
        else:
            self.llm = None
        
        # Session context storage
        self.session_contexts = {}
    
    def process_sync(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Synchronous version for testing"""
        return self._process_internal(user_input, context)
    
    async def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Async version with session context"""
        return self._process_internal(user_input, context)
    
    def _process_internal(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process with conversation flow and agent routing"""
        print(f"DEBUG: LLM available: {self.llm is not None}")
        print(f"DEBUG: GOOGLE_API_KEY set: {os.getenv('GOOGLE_API_KEY') is not None}")
        
        if not self.llm:
            print("DEBUG: Fallback - No LLM available")
            return self._fallback_processing(user_input, context)
        
        try:
            # Step 1: Extract entities with session context
            extracted_info = self._extract_entities_with_context(user_input, context)
            print(f"DEBUG: Extracted info: {extracted_info}")
            
            # Step 2: Determine conversation intent
            intent_analysis = self._reason_conversation_intent(extracted_info, context, user_input)
            print(f"DEBUG: Intent analysis: {intent_analysis}")
            
            # Step 3: Route to specialized agent
            execution_result = ""
            parsed_entities = {}
            parsed_intent = {}
            
            try:
                # Extract JSON from response with extra text
                def extract_json(text):
                    text = text.strip()
                    # Remove markdown wrapper
                    if '```json' in text:
                        start = text.find('```json') + 7
                        end = text.find('```', start)
                        if end != -1:
                            text = text[start:end].strip()
                        else:
                            text = text[start:].strip()
                    
                    # Find JSON object boundaries
                    start_idx = text.find('{')
                    if start_idx != -1:
                        brace_count = 0
                        for i, char in enumerate(text[start_idx:], start_idx):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    return text[start_idx:i+1]
                    return text
                
                clean_extracted = extract_json(extracted_info)
                clean_intent = extract_json(intent_analysis)
                
                print(f"DEBUG: Clean extracted JSON: {clean_extracted}")
                print(f"DEBUG: Clean intent JSON: {clean_intent}")
                
                parsed_entities = json.loads(clean_extracted)
                parsed_intent = json.loads(clean_intent)
                
                print(f"DEBUG: Parsed entities: {parsed_entities}")
                print(f"DEBUG: Parsed intent: {parsed_intent}")
                
                intent_type = parsed_intent.get('primary_intent', 'search')
                
                if intent_type in ['search', 'availability_check']:
                    execution_result = self._call_search_agent_sync(parsed_entities, context)
                elif intent_type in ['price_check', 'price_inquiry']:
                    execution_result = self._call_price_agent_sync(parsed_entities, context)
                elif intent_type == 'booking':
                    execution_result = self._call_booking_agent_sync(parsed_entities, context)
                elif intent_type.startswith('request_') or intent_type.startswith('book_') or intent_type == 'confirm_service_payment':
                    # Truyền thêm thông tin SMS code từ parsed_intent nếu có
                    if intent_type == 'confirm_service_payment' and parsed_intent.get('sms_code'):
                        parsed_entities['sms_code'] = parsed_intent['sms_code']
                    execution_result = self._call_service_agent_sync(parsed_entities, context, intent_type)
                    
            except Exception as e:
                print(f"DEBUG: Agent routing failed: {e}")
                print(f"DEBUG: Raw extracted_info: {repr(extracted_info)}")
                print(f"DEBUG: Raw intent_analysis: {repr(intent_analysis)}")
                parsed_entities = {}
                parsed_intent = {}
            
            # Step 4: Synthesize conversation response
            all_context = f"""
            Current Input: {user_input}
            Session Context: {json.dumps(context or {}, ensure_ascii=False)}
            Extracted Information: {extracted_info}
            Intent Analysis: {intent_analysis}
            Agent Result: {execution_result}
            """
            
            final_response = self._synthesize_conversation_response(all_context)
            
            # Step 5: Update session context  
            updated_context = self._update_session_context(context, parsed_entities, execution_result)
            
            return {
                "success": True,
                "response": final_response,
                "reasoning_steps": [
                    {"step": "extract", "result": extracted_info},
                    {"step": "reason", "result": intent_analysis},
                    {"step": "execute", "result": execution_result},
                    {"step": "synthesize", "result": final_response}
                ],
                "extracted_info": updated_context
            }
            
        except Exception as e:
            print(f"DEBUG: Exception in _process_internal: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_processing(user_input, context)
    
    def _extract_entities_with_context(self, input_text: str, context: Dict[str, Any] = None) -> str:
        """Extract entities with session context awareness"""
        # Fallback extraction linh hoạt với context awareness
        def fallback_extract(text, ctx=None):
            import re
            
            # Lấy thông tin từ context trước
            existing_locations = (ctx or {}).get('locations', {}) if ctx else {}
            existing_time = (ctx or {}).get('time', {}) if ctx else {}
            
            # Extract locations linh hoạt
            from_city = existing_locations.get('from', '')
            to_city = existing_locations.get('to', '')
            
            # Mở rộng patterns nhận diện địa điểm
            location_patterns = [
                r"từ\s+([^\sđ]+)\s+đến\s+([^\s]+)",  # từ X đến Y
                r"bay\s+từ\s+([^\sđ]+)\s+đến\s+([^\s]+)",  # bay từ X đến Y
                r"([^\s]+)\s+đến\s+([^\s]+)",  # X đến Y
                r"đi\s+([^\s]+)",  # đi X (chỉ có điểm đến)
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, text.lower())
                if match:
                    try:
                        if len(match.groups()) == 2:
                            from_raw, to_raw = match.groups()
                            normalized_from = self._normalize_city(from_raw.strip()) if hasattr(self, '_normalize_city') else from_raw.strip().title()
                            normalized_to = self._normalize_city(to_raw.strip()) if hasattr(self, '_normalize_city') else to_raw.strip().title()
                            from_city = normalized_from or from_city
                            to_city = normalized_to or to_city
                        else:  # chỉ có điểm đến
                            to_raw = match.group(1)
                            normalized_to = self._normalize_city(to_raw.strip()) if hasattr(self, '_normalize_city') else to_raw.strip().title()
                            to_city = normalized_to or to_city
                    except (AttributeError, IndexError) as e:
                        print(f"DEBUG: Location extraction error: {e}")
                        continue
                    break
            
            # Extract date linh hoạt
            date = existing_time.get('date', '')
            time_preference = existing_time.get('time_preference', '')
            
            # Mở rộng patterns thời gian
            time_patterns = {
                r"hôm nay|today": "hôm nay",
                r"ngày mai|tomorrow": "ngày mai",
                r"tuần sau|next week": "tuần sau",
                r"tháng sau|next month": "tháng sau",
                r"\d{1,2}/\d{1,2}/\d{4}": None,  # sẽ extract exact date
                r"sáng|morning": "sáng",
                r"chiều|afternoon": "chiều",
                r"tối|evening": "tối"
            }
            
            text_lower = text.lower()
            for pattern, value in time_patterns.items():
                if re.search(pattern, text_lower):
                    if value:
                        if pattern in [r"sáng|morning", r"chiều|afternoon", r"tối|evening"]:
                            time_preference = value
                        else:
                            date = value
                    else:  # exact date
                        date_match = re.search(pattern, text)
                        if date_match:
                            date = date_match.group()
            
            # Extract preferences linh hoạt
            price_patterns = {
                r"rẻ nhất|cheapest|giá rẻ": "cheapest",
                r"đắt nhất|expensive|cao cấp": "expensive",
                r"trung bình|medium": "medium"
            }
            
            price_range = ""
            for pattern, value in price_patterns.items():
                if re.search(pattern, text_lower):
                    price_range = value
                    break
            
            # Extract passengers safely
            passengers = 1
            try:
                passenger_match = re.search(r"(\d+)\s*người|for\s*(\d+)", text_lower)
                if passenger_match:
                    passenger_num = passenger_match.group(1) or passenger_match.group(2)
                    if passenger_num and passenger_num.isdigit():
                        passengers = max(1, min(int(passenger_num), 10))  # giới hạn 1-10
            except (ValueError, AttributeError) as e:
                print(f"DEBUG: Passenger extraction error: {e}")
                passengers = 1
            
            # Extract intent signals linh hoạt
            intent_keywords = {
                "search": ["tìm", "search", "có", "kiểm tra", "xem", "hiện thị", "cho tôi xem"],
                "booking": ["đặt vé", "đặt chỗ", "book", "mua vé", "order"],
                "price": ["giá", "price", "cost", "bao nhiêu"],
                "info": ["thông tin", "info", "chi tiết", "detail"]
            }
            
            intent_signals = []
            for intent_type, keywords in intent_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    intent_signals.append(intent_type)
            
            return {
                "locations": {"from": from_city, "to": to_city},
                "time": {"date": date, "time_preference": time_preference},
                "passengers": passengers,
                "preferences": {"price_range": price_range},
                "intent_signals": intent_signals,
                "conversation_type": "search"
            }
        
        if not self.llm:
            return json.dumps(fallback_extract(input_text, context), ensure_ascii=False)
        
        context_info = json.dumps(context or {}, ensure_ascii=False)
        
        prompt = f"""
        Bạn là AI chuyên trích xuất thông tin du lịch từ cuộc hội thoại tiếng Việt tự nhiên.
        
        Câu hiện tại: "{input_text}"
        Context trước: {context_info}
        
        HÃY PHÂN TÍCH LINH HOẠT:
        
        1. Địa điểm: Tìm bất kỳ địa danh nào (thành phố, quốc gia, vùng miền)
        2. Thời gian: Hiểu mọi cách nói về thời gian (tương đối, tuyệt đối, mùa vụ)
        3. Sở thích: Bắt mọi yêu cầu về giá, chất lượng, tiện ích
        4. Ý định: Hiểu ý định thực sự của người dùng
        
        KẾT HỢP THÔNG MINH:
        - Nếu context có thông tin, hãy kết hợp với câu mới
        - Ưu tiên thông tin mới nếu rõ ràng hơn
        - Giữ thông tin cũ nếu câu mới không thay đổi
        
        TRẢ VỀ JSON CHÍNH XÁC:
        {{
            "locations": {{"from": "[tên địa điểm xuất phát]", "to": "[tên địa điểm đến]"}},
            "time": {{"date": "[ngày/thời gian]", "time_preference": "[giờ/buổi]"}},
            "passengers": [số người],
            "preferences": {{"price_range": "[yêu cầu giá]"}},
            "intent_signals": ["[các từ khóa quan trọng]"],
            "conversation_type": "search"
        }}
        
        LƯU Ý: Chỉ điền thông tin nếu thực sự có trong câu hoặc context. Để trống nếu không có.
        """
        
        try:
            response = self.llm.invoke(prompt)
            # Validate response is valid JSON
            if hasattr(response, 'content'):
                test_parse = json.loads(response.content)
                return response.content
            else:
                # Handle different response formats
                content = str(response)
                test_parse = json.loads(content)
                return content
        except Exception as e:
            print(f"DEBUG: LLM extraction failed: {e}")
            # Fallback to regex extraction
            return json.dumps(fallback_extract(input_text, context), ensure_ascii=False)
    
    def _normalize_city(self, city_raw: str) -> str:
        """Chuẩn hóa tên thành phố linh hoạt"""
        if not city_raw:
            return ""
            
        city_map = {
            # HCM variants
            "hcm": "Ho Chi Minh City", "tphcm": "Ho Chi Minh City", 
            "sài gòn": "Ho Chi Minh City", "saigon": "Ho Chi Minh City",
            "tp.hcm": "Ho Chi Minh City", "ho chi minh": "Ho Chi Minh City",
            
            # Hanoi variants  
            "hn": "Hanoi", "hanoi": "Hanoi", "hà nội": "Hanoi",
            "ha noi": "Hanoi", "thủ đô": "Hanoi",
            
            # Da Nang variants
            "dn": "Da Nang", "đà nẵng": "Da Nang", "da nang": "Da Nang",
            "danang": "Da Nang",
            
            # Other cities
            "nha trang": "Nha Trang", "nt": "Nha Trang",
            "đà lạt": "Da Lat", "dalat": "Da Lat",
            "phú quốc": "Phu Quoc", "phu quoc": "Phu Quoc",
            "cần thơ": "Can Tho", "can tho": "Can Tho"
        }
        
        city_lower = city_raw.lower().strip()
        return city_map.get(city_lower, city_raw.title())
    
    def _reason_conversation_intent(self, extracted_info: str, context: Dict[str, Any] = None, user_input: str = "") -> str:
        """Determine conversation intent for agent routing"""
        if not self.llm:
            return '{"primary_intent": "search", "ready_for_action": false}'
        
        # Kiểm tra linh hoạt về dịch vụ dựa trên context
        user_lower = user_input.lower()
        
        # Dịch vụ keywords mở rộng
        service_patterns = {
            "hotel": ["khách sạn", "hotel", "phòng", "lưu trú", "nơi ở", "chỗ ở", "resort"],
            "transfer": ["xe", "taxi", "grab", "transfer", "đưa đón", "di chuyển", "vận chuyển"],
            "tour": ["tour", "du lịch", "tham quan", "khám phá", "hành trình", "đi chơi"],
            "insurance": ["bảo hiểm", "insurance", "bảo vệ"]
        }
        
        # Kiểm tra payment confirmation cho services
        import re
        if re.search(r"\b\d{6}\b", user_lower):  # 6-digit SMS code
            sms_match = re.search(r"\b(\d{6})\b", user_input)
            if sms_match:
                return json.dumps({
                    "primary_intent": "confirm_service_payment",
                    "target_agent": "ServiceAgent",
                    "ready_for_action": True,
                    "confidence": 0.95,
                    "sms_code": sms_match.group(1)
                }, ensure_ascii=False)
        
        # Kiểm tra context linh hoạt - nhiều nguồn khác nhau
        has_travel_context = False
        if context:
            # Kiểm tra nhiều nguồn context
            travel_indicators = [
                context.get('last_search_result'),
                context.get('completed_booking'),
                context.get('current_destination'),
                context.get('locations', {}).get('to'),
                context.get('locations', {}).get('from')
            ]
            
            # Hoặc tìm trong bất kỳ nested object nào
            for key, value in context.items():
                if isinstance(value, dict):
                    if any(k in ['flight', 'destination', 'to_city', 'from_city', 'airline'] for k in value.keys()):
                        travel_indicators.append(True)
                elif isinstance(value, str) and any(word in value.lower() for word in ['flight', 'vietjet', 'hanoi', 'ho chi minh', 'booking', 'destination']):
                    travel_indicators.append(True)
            
            has_travel_context = any(travel_indicators)
        
        # Nếu có context du lịch và hỏi về dịch vụ
        for service_type, keywords in service_patterns.items():
            if any(keyword in user_lower for keyword in keywords):
                # Kiểm tra nếu là booking request
                is_booking = any(booking_word in user_lower for booking_word in ["đặt", "book", "mua", "order", "chọn"])
                
                # Nếu có travel context HOẶC là booking request rõ ràng
                if has_travel_context or is_booking:
                    intent_name = f"book_{service_type}" if is_booking else f"request_{service_type}"
                    
                    return json.dumps({
                        "primary_intent": intent_name,
                        "target_agent": "ServiceAgent",
                        "ready_for_action": True,
                        "confidence": 0.9,
                        "service_type": service_type,
                        "is_booking": is_booking
                    }, ensure_ascii=False)
        
        context_info = json.dumps(context or {}, ensure_ascii=False)
        
        prompt = f"""
        Xác định intent để route đến agent phù hợp:
        
        Thông tin: {extracted_info}
        Session context: {context_info}
        User input: "{user_input}"
        
        QUY TẮC PHÂN BIỆT:
        - Nếu có "tìm", "xem", "hiển thị", "cho tôi" + "vé" → "search" (SearchAgent)
        - Nếu có "đặt vé", "mua vé", "book" → "booking" (BookingAgent)
        - Nếu có "giá", "bao nhiều tiền" → "price_check" (PriceAgent)
        - Nếu có "còn vé", "có chỗ" → "availability_check" (SearchAgent)
        
        Intent mapping:
        - "availability_check": "Còn vé không?" → SearchAgent
        - "price_check": "Giá vé bao nhiều?" → PriceAgent  
        - "search": "Tìm/Xem chuyến bay" → SearchAgent
        - "booking": "Đặt vé" → BookingAgent
        
        Trả về JSON:
        {{
            "primary_intent": "",
            "target_agent": "SearchAgent/PriceAgent/BookingAgent",
            "ready_for_action": true/false,
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
        except Exception as e:
            print(f"DEBUG: Intent analysis failed: {e}")
            return '{"primary_intent": "search", "target_agent": "SearchAgent", "ready_for_action": false}'
    
    def _call_search_agent_sync(self, entities: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Route to SearchAgent"""
        try:
            from agents.search_agent import SearchAgent
            from models.schemas import AgentRequest, ConversationContext
            
            locations = entities.get('locations', {}) or (context or {}).get('locations', {})
            time_info = entities.get('time', {}) or (context or {}).get('time', {})
            
            slots = {
                'from_city': locations.get('from', ''),
                'to_city': locations.get('to', ''),
                'date': time_info.get('date', ''),
                'time_preference': time_info.get('time_preference', ''),
                'passengers': entities.get('passengers', 1),
                'user_input': f"Tìm chuyến bay từ {locations.get('from', '')} đến {locations.get('to', '')} {entities.get('preferences', {}).get('price_range', '')}"
            }
            
            conv_context = ConversationContext(user_id="session_user")
            request = AgentRequest(
                intent="flight_search",
                user_input=f"Tìm chuyến bay từ {slots['from_city']} đến {slots['to_city']}",
                slots=slots,
                context=conv_context
            )
            
            search_agent = SearchAgent()
            result = search_agent.process_sync(request) if hasattr(search_agent, 'process_sync') else search_agent.process(request)
            
            return json.dumps({
                "success": result.success,
                "agent": "SearchAgent",
                "data": result.data,
                "message": result.message
            })
            
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    def _call_price_agent_sync(self, entities: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Route to PriceAgent"""
        try:
            from models.schemas import AgentRequest, ConversationContext
            
            locations = entities.get('locations', {}) or (context or {}).get('locations', {})
            time_info = entities.get('time', {}) or (context or {}).get('time', {})
            
            user_input = f"Kiểm tra giá vé từ {locations.get('from', '')} đến {locations.get('to', '')}"
            if time_info.get('date'):
                user_input += f" ngày {time_info['date']}"
            if time_info.get('time_preference'):
                user_input += f" lúc {time_info['time_preference']}"
            if any('rẻ' in signal for signal in entities.get('intent_signals', [])):
                user_input += " giá rẻ nhất"
            
            conv_context = ConversationContext(user_id="session_user")
            request = AgentRequest(
                intent="price_check",
                user_input=user_input,
                slots={},
                context=conv_context
            )
            
            if PriceAgent is None:
                return json.dumps({"success": False, "error": "PriceAgent not available"})
            price_agent = PriceAgent()
            if hasattr(price_agent, 'process_sync'):
                result = price_agent.process_sync(request)
            else:
                # Skip async call in sync context
                result = type('Result', (), {'success': False, 'data': {}, 'message': 'PriceAgent requires async context'})()
            
            return json.dumps({
                "success": result.success,
                "agent": "PriceAgent",
                "data": result.data,
                "message": result.message
            })
            
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    def _call_booking_agent_sync(self, entities: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Route to BookingAgent"""
        try:
            from agents.booking_agent import BookingAgent
            from models.schemas import AgentRequest, ConversationContext
            
            # Get flight_id from context or use default
            flight_id = (context or {}).get('selected_flight_id') or 'VJ123'
            
            conv_context = ConversationContext(user_id="session_user")
            request = AgentRequest(
                intent="booking",
                user_input=f"Đặt vé chuyến bay {flight_id}",
                slots={'flight_id': flight_id},
                context=conv_context
            )
            
            booking_agent = BookingAgent()
            result = booking_agent.process_sync(request) if hasattr(booking_agent, 'process_sync') else booking_agent.process(request)
            
            return json.dumps({
                "success": result.success,
                "agent": "BookingAgent", 
                "data": result.data,
                "message": result.message
            })
            
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    def _call_service_agent_sync(self, entities: Dict[str, Any], context: Dict[str, Any] = None, intent_type: str = "") -> str:
        """Route to Service Agent for hotel/transfer/tour requests"""
        try:
            # Lấy thông tin điểm đến thông minh từ nhiều nguồn
            destination = ""
            origin = ""
            
            if context:
                # Ưu tiên 1: current_destination (từ booking hoàn thành)
                destination = context.get('current_destination', '')
                origin = context.get('current_origin', '')
                
                # Ưu tiên 2: completed_booking
                if not destination and context.get('completed_booking'):
                    booking_info = context['completed_booking']
                    if isinstance(booking_info, dict):
                        travel_info = booking_info.get('travel_info', {})
                        destination = travel_info.get('destination', travel_info.get('to_city', ''))
                        origin = travel_info.get('origin', travel_info.get('from_city', ''))
                
                # Ưu tiên 3: last_search_result
                if not destination and context.get('last_search_result'):
                    search_data = context['last_search_result']
                    if isinstance(search_data, dict) and search_data.get('data', {}).get('flights'):
                        flights = search_data['data']['flights']
                        if flights:
                            flight = flights[0]
                            destination = flight.get('to_city', flight.get('destination', ''))
                            origin = flight.get('from_city', flight.get('origin', ''))
                
                # Ưu tiên 4: locations
                if not destination and context.get('locations'):
                    locations = context['locations']
                    destination = locations.get('to', '')
                    origin = locations.get('from', '')
                
                # Fallback: tìm trong toàn bộ context
                if not destination:
                    def find_destination_in_data(data, path="", depth=0):
                        # Giới hạn độ sâu để tránh infinite recursion
                        if depth > 5:
                            return None
                            
                        try:
                            if isinstance(data, dict):
                                for key, value in data.items():
                                    if key in ['to_city', 'destination', 'current_destination'] and value:
                                        return str(value)
                                    elif isinstance(value, (dict, list)):
                                        result = find_destination_in_data(value, f"{path}.{key}", depth + 1)
                                        if result:
                                            return result
                            elif isinstance(data, list) and len(data) < 100:  # giới hạn size
                                for i, item in enumerate(data[:10]):  # chỉ check 10 items đầu
                                    result = find_destination_in_data(item, f"{path}[{i}]", depth + 1)
                                    if result:
                                        return result
                            elif isinstance(data, str) and len(data) < 1000:  # giới hạn length
                                cities = {'hanoi': 'Hanoi', 'hà nội': 'Hanoi', 'ho chi minh': 'Ho Chi Minh City', 'hcm': 'Ho Chi Minh City', 'tp.hcm': 'Ho Chi Minh City'}
                                data_lower = data.lower()
                                for city_key, city_name in cities.items():
                                    if city_key in data_lower:
                                        return city_name
                        except Exception as e:
                            print(f"DEBUG: Error in find_destination_in_data: {e}")
                        return None
                    
                    destination = find_destination_in_data(context) or destination
            
            # Kiểm tra loại request
            if intent_type == 'confirm_service_payment':
                # Xử lý xác nhận thanh toán - lấy SMS code từ entities
                sms_code = entities.get('sms_code', '')
                # Nếu không có trong entities, thử tìm trong context
                if not sms_code and context:
                    # Tìm SMS code trong context hoặc từ intent analysis trước đó
                    for key, value in context.items():
                        if isinstance(value, str) and len(value) == 6 and value.isdigit():
                            sms_code = value
                            break
                payment_result = self._process_service_payment_confirmation(sms_code, context)
                return json.dumps(payment_result)
            
            service_type = intent_type.replace('request_', '').replace('book_', '')
            
            # Mock service data dựa trên điểm đến
            service_data = self._get_service_data(service_type, destination)
            
            # Kiểm tra nếu là booking request
            is_booking = intent_type.startswith('book_')
            
            if is_booking:
                # Xử lý booking service
                booking_result = self._process_service_booking(service_type, destination, service_data, context)
                return json.dumps(booking_result)
            else:
                # Chỉ hiển thị thông tin
                return json.dumps({
                    "success": True,
                    "agent": "ServiceAgent",
                    "service_type": service_type,
                    "destination": destination,
                    "origin": origin,
                    "data": service_data,
                    "message": f"Thông tin {service_type} tại {destination or 'destination'}"
                })
            
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    def _get_service_data(self, service_type: str, destination: str) -> Dict[str, Any]:
        """Get mock service data based on destination"""
        # Tạo data linh hoạt dựa trên destination
        if service_type == "hotel":
            return self._generate_hotel_data(destination)
        elif service_type == "transfer":
            return self._generate_transfer_data(destination, "")
        elif service_type == "tour":
            return self._generate_tour_data(destination)
        elif service_type == "insurance":
            return self._generate_insurance_data()
        return {}
    
    def _process_service_booking(self, service_type: str, destination: str, service_data: Dict, context: Dict) -> Dict[str, Any]:
        """Xử lý booking cho dịch vụ SOVICO"""
        try:
            from datetime import datetime
            import random
            
            # Tạo booking ID
            booking_id = f"SOVICO_{service_type.upper()}_{random.randint(1000, 9999)}"
            
            # Lấy service đầu tiên (hoặc service được chọn)
            services = service_data.get(f"{service_type}s", [])
            if not services:
                return {
                    "success": False,
                    "message": f"Không tìm thấy {service_type} phù hợp tại {destination}"
                }
            
            selected_service = services[0]  # Chọn service đầu tiên
            
            # Tạo payment code và booking info
            payment_code = f"PAY_{service_type.upper()}_{random.randint(100000, 999999)}"
            sms_code = f"{random.randint(100000, 999999)}"
            
            booking_info = {
                "booking_id": booking_id,
                "payment_code": payment_code,
                "service_type": service_type,
                "service_name": selected_service.get('name'),
                "destination": destination,
                "price": selected_service.get('price'),
                "booking_date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "status": "pending_payment",
                "booking_code": selected_service.get('booking_code'),
                "contact_info": "Hotline SOVICO: 1900-1234",
                "sms_code": sms_code,
                "payment_deadline": "15 phút"
            }
            
            # Tạo response message
            if service_type == "hotel":
                message = f"🎉 ĐẶT PHÒNG THÀNH CÔNG!\n\n"
                message += f"🏨 **{selected_service['name']}**\n"
                message += f"📍 {selected_service['location']}\n"
                message += f"⭐ {selected_service['rating']} sao\n"
                message += f"💰 Giá: {selected_service['price']}\n"
                message += f"🆔 Mã đặt phòng: {booking_id}\n\n"
                message += f"📞 Liên hệ: {booking_info['contact_info']}\n"
                message += f"✅ Xác nhận qua email trong 15 phút"
                
            elif service_type == "transfer":
                message = f"🎉 ĐẶT XE THÀNH CÔNG!\n\n"
                message += f"🚗 **{selected_service['type']}**\n"
                message += f"🛣️ {selected_service['route']}\n"
                message += f"⏱️ Thời gian: {selected_service['duration']}\n"
                message += f"💰 Giá: {selected_service['price']}\n"
                message += f"🆔 Mã đặt xe: {booking_id}\n\n"
                message += f"📞 Liên hệ tài xế: {booking_info['contact_info']}\n"
                message += f"🕐 Xe sẽ đến đúng giờ bay của bạn"
                
            elif service_type == "tour":
                message = f"🎉 ĐẶT TOUR THÀNH CÔNG!\n\n"
                message += f"🎯 **{selected_service['name']}**\n"
                message += f"⏰ Thời gian: {selected_service['duration']}\n"
                message += f"💰 Giá: {selected_service['price']}\n"
                message += f"🆔 Mã đặt tour: {booking_id}\n\n"
                if 'highlights' in selected_service:
                    message += f"📍 Điểm tham quan: {', '.join(selected_service['highlights'][:3])}\n"
                message += f"📞 Liên hệ hướng dẫn viên: {booking_info['contact_info']}"
            
            else:
                message = f"🎉 ĐẶT DỊCH VỤ THÀNH CÔNG!\n\n"
                message += f"🆔 Mã đặt: {booking_id}\n"
                message += f"📞 Liên hệ: {booking_info['contact_info']}"
            
            # Tạo payment message
            message = f"💳 XÁC THỰC THANH TOÁN {service_type.upper()}\n\n"
            message += f"💰 Tổng tiền: {selected_service.get('price')}\n"
            message += f"📱 Mã xác thực đã gửi đến ******\n\n"
            message += f"🔐 Vui lòng nhập mã 6 số để xác nhận thanh toán cho booking: {booking_id}\n\n"
            message += f"⏰ Mã có hiệu lực trong 15 phút\n\n"
            message += f"📝 Mã test: {sms_code}"
            
            return {
                "success": True,
                "agent": "ServicePaymentAgent",
                "service_type": service_type,
                "booking_info": booking_info,
                "message": message,
                "payment_required": True,
                "sms_code": sms_code,
                "suggestions": [f"🔢 Nhập mã: {sms_code}", "❌ Hủy thanh toán"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Lỗi khi đặt {service_type}: {str(e)}",
                "suggestions": ["🔄 Thử lại", "📞 Liên hệ hỗ trợ"]
            }
    
    def _process_service_payment_confirmation(self, sms_code: str, context: Dict) -> Dict[str, Any]:
        """Xử lý xác nhận thanh toán cho dịch vụ"""
        try:
            import random
            
            # Tạo confirmation code
            confirmation_code = f"SOVICO_CONF_{random.randint(1000, 9999)}"
            
            # Success message
            message = f"🎉 THANH TOÁN THÀNH CÔNG!\n\n"
            message += f"✅ Xác thực hoàn tất\n"
            message += f"🎫 Mã xác nhận: {confirmation_code}\n"
            message += f"📧 Email xác nhận đã gửi\n\n"
            
            message += f"📝 Hướng dẫn:\n"
            message += f"- Liên hệ SOVICO: 1900-1234\n"
            message += f"- Mang theo mã xác nhận khi sử dụng\n"
            message += f"- Kiểm tra email để biết thêm chi tiết\n\n"
            
            message += f"🎉 Cảm ơn bạn đã sử dụng dịch vụ SOVICO!"
            
            return {
                "success": True,
                "agent": "ServicePaymentConfirmation",
                "confirmation_code": confirmation_code,
                "message": message,
                "payment_completed": True,
                "suggestions": ["🏨 Đặt thêm dịch vụ", "📞 Liên hệ hỗ trợ", "📋 Xem booking"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Lỗi xác nhận thanh toán: {str(e)}",
                "suggestions": ["🔄 Thử lại", "📞 Liên hệ hỗ trợ"]
            }
    
    def _generate_hotel_data(self, destination: str) -> Dict[str, Any]:
        """Tạo data khách sạn linh hoạt theo destination"""
        dest_lower = destination.lower()
        
        if "hanoi" in dest_lower or "hà nội" in dest_lower:
            return {
                "hotels": [
                    {
                        "name": "Lotte Hotel Hanoi", 
                        "rating": 5, 
                        "price": "2,500,000đ/đêm", 
                        "location": "Ba Đình, Hà Nội",
                        "amenities": ["Spa cao cấp", "Hồ bơi vô cực", "Gym 24/7", "Nhà hàng Michelin"],
                        "distance_center": "2km từ trung tâm",
                        "booking_code": "LOTTE_HN_001"
                    },
                    {
                        "name": "Hilton Hanoi Opera", 
                        "rating": 5, 
                        "price": "2,200,000đ/đêm", 
                        "location": "Hoàn Kiếm, Hà Nội",
                        "amenities": ["Trung tâm thương mại", "Hồ bơi", "Spa", "Nhà hàng quốc tế"],
                        "distance_center": "500m từ Hồ Hoàn Kiếm",
                        "booking_code": "HILTON_HN_002"
                    },
                    {
                        "name": "Hotel Nikko Hanoi", 
                        "rating": 4, 
                        "price": "1,800,000đ/đêm", 
                        "location": "Tây Hồ, Hà Nội",
                        "amenities": ["View hồ Tây", "Nhà hàng Nhật Bản", "Spa", "Gym"],
                        "distance_center": "3km từ trung tâm",
                        "booking_code": "NIKKO_HN_003"
                    }
                ]
            }
        elif "ho chi minh" in dest_lower or "hcm" in dest_lower or "saigon" in dest_lower:
            return {
                "hotels": [
                    {
                        "name": "Park Hyatt Saigon", 
                        "rating": 5, 
                        "price": "3,000,000đ/đêm", 
                        "location": "Quận 1, TP.HCM",
                        "amenities": ["Spa đẳng cấp thế giới", "Hồ bơi trên sân thượng", "Nhà hàng Park Lounge"],
                        "distance_center": "Trung tâm Quận 1",
                        "booking_code": "HYATT_SGN_001"
                    },
                    {
                        "name": "Caravelle Saigon", 
                        "rating": 5, 
                        "price": "2,800,000đ/đêm", 
                        "location": "Quận 1, TP.HCM",
                        "amenities": ["View thành phố tuyệt đẹp", "Saigon Saigon Bar", "Hồ bơi"],
                        "distance_center": "Gần Nhà hát Thành phố",
                        "booking_code": "CARAVELLE_SGN_002"
                    }
                ]
            }
        elif "da nang" in dest_lower or "đà nẵng" in dest_lower:
            return {
                "hotels": [
                    {"name": "InterContinental Danang", "rating": 5, "price": "2,200,000đ/đêm", "location": "Bãi biển Đà Nẵng"},
                    {"name": "Pullman Danang Beach Resort", "rating": 5, "price": "2,000,000đ/đêm", "location": "Bãi biển Đà Nẵng"}
                ]
            }
        else:
            return {
                "hotels": [
                    {
                        "name": f"SOVICO Hotel {destination}", 
                        "rating": 4, 
                        "price": "1,500,000đ/đêm", 
                        "location": f"Trung tâm {destination}",
                        "amenities": ["WiFi miễn phí", "Bữa sáng", "Gym"],
                        "distance_center": "Trung tâm thành phố",
                        "booking_code": f"SOVICO_{destination.upper()}_001"
                    }
                ]
            }
    
    def _generate_transfer_data(self, destination: str, origin: str = "") -> Dict[str, Any]:
        """Tạo data xe đưa đón linh hoạt"""
        return {
            "transfers": [
                {
                    "type": "Xe riêng SOVICO VIP", 
                    "price": "350,000đ", 
                    "duration": "45 phút", 
                    "route": f"Sân bay Nội Bài - Trung tâm {destination}",
                    "features": ["Xe sang", "Tài xế chuyên nghiệp", "Nước suối miễn phí"],
                    "booking_code": "TRANSFER_VIP_001"
                },
                {
                    "type": "Xe Limousine SOVICO", 
                    "price": "180,000đ", 
                    "duration": "60 phút", 
                    "route": f"Sân bay Nội Bài - {destination}",
                    "features": ["Ghế massage", "WiFi", "Điều hòa"],
                    "booking_code": "TRANSFER_LIMO_002"
                }
            ]
        }
    
    def _generate_tour_data(self, destination: str) -> Dict[str, Any]:
        """Tạo data tour linh hoạt"""
        dest_lower = destination.lower()
        
        if "hanoi" in dest_lower or "hà nội" in dest_lower:
            return {
                "tours": [
                    {
                        "name": "Tour Hà Nội Kinh đô 1000 năm", 
                        "price": "950,000đ/người", 
                        "duration": "8 giờ",
                        "highlights": ["Lăng Bác", "Chùa Một Cột", "Hồ Hoàn Kiếm", "Phố cổ 36 phố phường"],
                        "booking_code": "TOUR_HN_FULL_001"
                    },
                    {
                        "name": "Tour Ẩm thực Hà Nội", 
                        "price": "650,000đ/người", 
                        "duration": "4 giờ",
                        "highlights": ["Phở Bò", "Bún Chả", "Chè Lâm", "Bia hơi Tạ Hiện"],
                        "booking_code": "TOUR_HN_FOOD_002"
                    }
                ]
            }
        else:
            return {
                "tours": [
                    {
                        "name": f"Tour khám phá {destination}", 
                        "price": "800,000đ/người", 
                        "duration": "8 giờ",
                        "highlights": [f"Điểm tham quan nổi tiếng {destination}"],
                        "booking_code": f"TOUR_{destination.upper()}_001"
                    }
                ]
            }
    
    def _generate_insurance_data(self) -> Dict[str, Any]:
        """Tạo data bảo hiểm"""
        return {
            "insurance": [
                {"name": "Bảo hiểm du lịch cơ bản", "price": "50,000đ", "coverage": "500 triệu đồng"},
                {"name": "Bảo hiểm du lịch cao cấp", "price": "100,000đ", "coverage": "1 tỷ đồng"}
            ]
        }
    
    def _synthesize_conversation_response(self, all_info: str) -> str:
        """Synthesize natural conversation response"""
        if not self.llm:
            return "Đã xử lý yêu cầu của bạn."
        
        from datetime import datetime
        current_date = datetime.now().strftime("%A, %d/%m/%Y")
        
        prompt = f"""
        Bạn là AI Trợ lý Du lịch SOVICO - chuyên gia vé VietJet Air và dịch vụ du lịch.
        
        === THÔNG TIN THỜI GIAN HIỆN TẠI ===
        Hôm nay là: {current_date}
        Luôn sử dụng thời gian thực tế này khi trả lời.
        
        === DỮ LIỆU ĐẦY ĐỦ CỦA CUỘC TRÒ CHUYỆN ===
        {all_info}
        
        === HƯỚNG DẪN PHÂN TÍCH VÀ TRẢ LỜI ===
        
        BƯỚC 1: PHÂN TÍCH DỮC LIỆU
        - Đọc kỹ "Current Input" - câu khách vừa nói
        - Đọc "Session Context" - thông tin đã biết từ trước (locations, time, preferences)
        - Đọc "Extracted Information" - thông tin mới trích xuất
        - Đọc "Agent Result" - kết quả tìm kiếm/kiểm tra giá/đặt vé
        
        BƯỚC 2: HIỂU Ý ĐỊNH KHÁCH HÀNG
        - Khách muốn tìm vé? Kiểm tra giá? Đặt vé? Gợi ý?
        - Có thông tin địa điểm chưa? (from/to)
        - Có thông tin thời gian chưa? (date/time)
        - Có yêu cầu đặc biệt? (giá rẻ, giờ cụ thể)
        
        BƯỚC 3: XửC LÝ KẾT QUẢ AGENT
        - Nếu Agent Result có "success": true và "flights" data:
          → Hiển thị thông tin chuyến bay VietJet cụ thể
          → Bao gồm: mã chuyến, giờ bay, giá vé, số ghế còn lại
        - Nếu Agent Result có "success": false:
          → Giải thích tại sao không tìm thấy
          → Gợi ý giải pháp khác
        - Nếu không có Agent Result:
          → Hỏi thông tin còn thiếu để tìm kiếm
        
        BƯỚC 4: TẠO RESPONSE THÔNG MINH
        - Sử dụng thông tin từ Session Context, KHÔNG hỏi lại
        - Nếu có kết quả tìm kiếm: trình bày rõ ràng, hấp dẫn
        - Nếu thiếu thông tin: hỏi cụ thể nhất
        - Luôn kết thúc bằng gợi ý hành động tiếp theo
        
        === QUY TẮC QUAN TRỌNG ===
        - CHỈ tư vấn VietJet Air cho vé máy bay
        - Có thể tư vấn khách sạn, combo, xe đưa đón
        - Tone thân thiện, chuyên nghiệp
        - Luôn nhấn mạnh là dịch vụ SOVICO
        
        BẮT ĐẦU PHÂN TÍCH VÀ TRẢ LỜI:
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except:
            return "Tôi hiểu yêu cầu của bạn về vé VietJet Air. Hãy cho tôi biết thêm thông tin nhé!"
    
    def _update_session_context(self, context: Dict[str, Any], entities: Dict[str, Any], execution_result: str) -> Dict[str, Any]:
        """Update session context for conversation continuity"""
        updated_context = context.copy() if context else {}
        
        # Update locations
        if entities.get('locations'):
            updated_context['locations'] = entities['locations']
        
        # Update time preferences
        if entities.get('time'):
            updated_context['time'] = entities['time']
        
        # Update preferences
        if entities.get('preferences'):
            updated_context['preferences'] = entities['preferences']
        
        # Store last search results
        if execution_result:
            try:
                result_data = json.loads(execution_result)
                if result_data.get('success'):
                    updated_context['last_search_result'] = result_data
                    
                    # Extract flight_id for booking
                    if result_data.get('data', {}).get('flights'):
                        flights = result_data['data']['flights']
                        if flights:
                            updated_context['selected_flight_id'] = flights[0].get('flight_id')
            except:
                pass
        
        return updated_context
    
    def _fallback_processing(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback when LLM is not available"""
        return {
            "success": True,
            "response": "Tôi hiểu yêu cầu của bạn. Hãy cho tôi biết thêm thông tin để hỗ trợ tốt hơn.",
            "reasoning_steps": [],
            "extracted_info": context or {}
        }