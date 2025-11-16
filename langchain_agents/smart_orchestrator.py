"""
Smart Orchestrator - Điều phối thông minh với LLM
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os

class SmartBookingOrchestrator:
    """Orchestrator sử dụng IntelligentReasoningAgent với system prompt"""
    
    def __init__(self, api_key: str = None, provider: str = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "gemini")
        from agents.intelligent_reasoning_agent import IntelligentReasoningAgent
        from agents.smart_intent_agent import smart_intent_agent
        from agents.booking_intent_agent import booking_intent_agent
        from agents.upselling_agent_v2 import upsell_agent
        from utils.context_storage import context_storage
        
        self.reasoning_agent = IntelligentReasoningAgent()
        self.smart_intent_agent = smart_intent_agent
        self.booking_intent_agent = booking_intent_agent
        self.upsell_agent = upsell_agent
        self.context_storage = context_storage
        
        # System prompt cho context
        self.system_context = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        current_date = datetime.now().strftime("%A, %d/%m/%Y")
        return f"""Bạn là trợ lý đặt vé máy bay thông minh của hệ sinh thái SOVICO.

THÔNG TIN THỜI GIAN:
- Hôm nay là: {current_date}
- Luôn sử dụng thời gian thực tế hiện tại

THÔNG TIN HỆ THỐNG:
- Bạn là trợ lý du lịch của hệ sinh thái SOVICO
- VỀ VÉ MÁY BAY: CHỈ tư vấn và đặt vé VIETJET AIR
- KHÔNG tư vấn hãng bay khác (Vietnam Airlines, Bamboo Airways, etc.)
- NGOÀI VÉ MÁY BAY: Có thể tư vấn khách sạn, resort, combo du lịch, voucher, xe đưa đón
- Nếu khách hỏi về hãng bay khác: "Về vé máy bay, tôi chỉ hỗ trợ VietJet Air - hãng bay chính thức của SOVICO"

NHIỆM VỤ:
- Hiểu yêu cầu của khách hàng bằng tiếng Việt tự nhiên
- Sử dụng multi-step reasoning để xử lý yêu cầu phức tạp
- Trả lời bằng tiếng Việt thân thiện, sử dụng emoji
- Đưa ra response tự nhiên và có ngữ cảnh

QUY TRÌNH THÔNG MINH:
1. Trích xuất thông tin từ yêu cầu
2. Phân tích ý định người dùng
3. Lập kế hoạch hành động
4. Thực hiện tìm kiếm/kiểm tra giá/đặt vé VietJet + tư vấn dịch vụ khác
5. Tổng hợp response hoàn chỉnh

CÁCH TRẢ LỜI:
- Thể hiện sự hiểu biết về yêu cầu
- Đưa ra thông tin cụ thể về VietJet và dịch vụ du lịch khác
- Hỏi thêm thông tin nếu cần
- Gợi ý bước tiếp theo rõ ràng

VÍ DỤ RESPONSE TỐT:
"Tôi hiểu bạn muốn bay về quê ăn Tết cho gia đình 4 người với giá tiết kiệm. Bạn về quê ở đâu để tôi tìm chuyến VietJet phù hợp nhé?"

"Tôi đã kiểm tra giá vé VietJet từ Hà Nội đến TP.HCM cho bạn. Giá rẻ nhất hiện tại là 1.200.000đ..."

"Về vé máy bay, tôi chỉ hỗ trợ VietJet Air - hãng bay chính thức của SOVICO. Nhưng tôi có thể tư vấn thêm khách sạn, combo du lịch nhé!"

QUAN TRỌNG:
- Luôn sử dụng thời gian thực tế hiện tại ({current_date})
- Tạo response tự nhiên và có ngữ cảnh
- Hiểu biết sâu về nhu cầu người dùng
- Về vé máy bay: CHỈ tư vấn VietJet Air
- Về du lịch: Tư vấn đầy đủ dịch vụ SOVICO
- Nhấn mạnh là dịch vụ của SOVICO"""
    
    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process message với smart intent detection và booking flow"""
        try:
            # Load session context from storage
            session_context = self.context_storage.load_context(user_id) or {}
            
            # Kiểm tra xem có đang trong quá trình booking không
            booking_session = session_context.get('booking_session') if session_context else None
            
            if booking_session and isinstance(booking_session, dict) and 'session_id' in booking_session:
                # Xử lý booking flow
                return await self._handle_booking_flow(user_id, message, booking_session)
            
            # Phân tích intent bằng SmartIntentAgent trước
            booking_decision = self.smart_intent_agent.should_proceed_with_booking(message, user_id)
            
            # Debug intent detection
            print(f"DEBUG: Booking decision: {booking_decision}")
            
            if booking_decision['should_book']:
                # Bắt đầu quá trình đặt vé
                return await self._start_booking_process(user_id, message)
            elif booking_decision.get('should_confirm'):
                # Hỏi xác nhận trước khi đặt vé
                return self._ask_booking_confirmation(message)
            else:
                # Xử lý bình thường (tìm kiếm, hỏi thông tin)
                result = await self.reasoning_agent.process(message, session_context)
            
                # Update session context cho search
                updated_context = session_context.copy() if session_context else {}
                
                if result.get("success") and result.get("extracted_info"):
                    new_info = result.get("extracted_info", {})
                    
                    # Safe merge locations
                    if new_info.get('locations'):
                        updated_context.setdefault('locations', {}).update(new_info['locations'])
                    
                    # Safe merge time info
                    if new_info.get('time'):
                        updated_context.setdefault('time', {}).update(new_info['time'])
                    
                    # Update other fields
                    for key in ['passengers', 'last_search_result', 'selected_flight_id']:
                        if key in new_info:
                            updated_context[key] = new_info[key]
                    
                    # Cập nhật context cho SmartIntentAgent
                    if new_info.get('last_search_result'):
                        self.smart_intent_agent.update_context(user_id, 'last_search', new_info['last_search_result'])
                    
                    # Lưu toàn bộ kết quả search cho booking
                    if result.get('success') and 'data' in result:
                        self.smart_intent_agent.update_context(user_id, 'last_search', result)
                    
                    self.context_storage.save_context(user_id, updated_context)
                
                # Generate contextual suggestions
                suggestions = self._generate_contextual_suggestions(message, result, updated_context)
                
                return {
                    "response": result.get("response", "Xin lỗi, tôi không hiểu yêu cầu của bạn."),
                    "suggestions": suggestions,
                    "context": {
                        "agent_type": "intelligent_reasoning", 
                        "user_id": user_id,
                        "session_context": updated_context
                    }
                }
            
        except Exception as e:
            return {
                "response": f"😅 Xin lỗi, có lỗi xảy ra: {str(e)}. Bạn có thể thử lại không?",
                "suggestions": ["🔄 Thử lại", "🆘 Hỗ trợ"],
                "context": {"error": str(e)}
            }
    
    def _generate_contextual_suggestions(self, user_message: str, result: Dict[str, Any], session_context: Dict[str, Any]) -> List[str]:
        """Generate contextual suggestions based on conversation flow"""
        if not session_context:
            session_context = {}
            
        # Safe access to context data
        locations = session_context.get('locations', {})
        has_locations = bool(locations.get('from') and locations.get('to'))
        has_search_results = bool(session_context.get('last_search_result'))
        
        user_lower = user_message.lower()
        result_str = str(result)
        
        # Kiểm tra nếu là yêu cầu dịch vụ Sovico
        sovico_services = ["khách sạn", "hotel", "xe đưa đón", "transfer", "tour", "bảo hiểm"]
        if any(service in user_lower for service in sovico_services):
            return ["🏨 Khách sạn Sovico", "🚗 Xe đưa đón", "🎯 Tour Sovico", "🛡️ Bảo hiểm"]
        
        if "còn vé" in user_lower or "availability" in result_str:
            return ["💰 Giá vé bao nhiêu?", "⏰ Giờ bay khác?", "📅 Ngày khác?", "🎯 Đặt vé ngay"]
        elif "giá" in user_lower:
            return ["🎯 Đặt vé này", "⏰ Xem giờ khác", "📅 Xem ngày khác", "🔍 So sánh giá"]
        elif "đặt vé" in user_lower or "booking" in result_str:
            return ["🏨 Thêm khách sạn Sovico", "🚗 Đặt xe đưa đón", "📋 Xem thông tin booking", "💳 Hướng dẫn thanh toán"]
        elif has_locations and not has_search_results:
            return ["🔍 Tìm chuyến bay", "💰 Kiểm tra giá", "⏰ Chọn giờ bay", "📅 Chọn ngày"]
        else:
            return ["✈️ HN → SGN ngày mai", "💰 Giá vé rẻ nhất", "🔍 Tìm chuyến bay", "🎁 Combo du lịch"]
    
    def _safe_update_booking_context(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Cập nhật booking session một cách an toàn, không ảnh hưởng context khác"""
        try:
            session_context = self.context_storage.load_context(user_id) or {}
            
            # Đảm bảo booking_session tồn tại và là dict
            if 'booking_session' not in session_context:
                print(f"DEBUG: No booking_session found for user {user_id}")
                return False
            
            if not isinstance(session_context['booking_session'], dict):
                print(f"DEBUG: booking_session is not dict for user {user_id}")
                return False
            
            # Chỉ cập nhật booking_session, giữ nguyên tất cả context khác
            session_context['booking_session'].update(updates)
            
            # Lưu lại toàn bộ context an toàn
            self.context_storage.save_context(user_id, session_context)
            print(f"DEBUG: Updated booking_session for user {user_id}: {updates}")
            return True
            
        except Exception as e:
            print(f"Error updating booking session: {e}")
            return False
    
    def _safe_remove_booking_context(self, user_id: str) -> bool:
        """Xóa booking session một cách an toàn, giữ nguyên tất cả context khác"""
        try:
            session_context = self.context_storage.load_context(user_id) or {}
            
            # Chỉ xóa booking_session (flow đặt vé), giữ nguyên tất cả thông tin khác
            if 'booking_session' in session_context:
                del session_context['booking_session']
                
                # Đảm bảo không mất bất kỳ thông tin nào khác
                self.context_storage.save_context(user_id, session_context)
                print(f"DEBUG: Removed booking_session for user {user_id}, kept other context")
            
            return True
            
        except Exception as e:
            print(f"Error removing booking session: {e}")
            return False
    
    async def _start_booking_process(self, user_id: str, message: str) -> Dict[str, Any]:
        """Bắt đầu quy trình đặt vé"""
        
        # Phát hiện intent và trích xuất thông tin chuyến bay
        intent_result = self.smart_intent_agent.analyze_intent(message, user_id=user_id)
        flight_info = intent_result.get('extracted_info', {})
        
        print(f"DEBUG _start_booking_process: intent_result={intent_result}")
        print(f"DEBUG _start_booking_process: flight_info={flight_info}")
        
        # Bắt đầu booking process
        booking_result = self.booking_intent_agent.start_booking_process(flight_info)
        
        print(f"DEBUG _start_booking_process: booking_result={booking_result}")
        
        if booking_result['success']:
            # Lưu session booking vào context (không ảnh hưởng context khác)
            session_context = self.context_storage.load_context(user_id) or {}
            session_context['booking_session'] = {
                'session_id': booking_result['session_id'],
                'step': 'collect_phone',
                'flight_info': flight_info
            }
            self.context_storage.save_context(user_id, session_context)
            
            print(f"DEBUG _start_booking_process: Saved booking session for user {user_id}")
            
            return {
                "response": booking_result['message'],
                "suggestions": ["📱 Nhập SĐT", "❌ Hủy đặt vé"],
                "context": {
                    "agent_type": "booking_process",
                    "step": "collect_phone",
                    "session_id": booking_result['session_id']
                }
            }
        else:
            print(f"DEBUG _start_booking_process: Booking failed: {booking_result}")
            return {
                "response": booking_result.get('message', 'Không thể bắt đầu đặt vé. Vui lòng thử lại.'),
                "suggestions": ["🔍 Tìm chuyến bay", "🆘 Hỗ trợ"]
            }
    
    def _ask_booking_confirmation(self, message: str) -> Dict[str, Any]:
        """Hỏi xác nhận trước khi đặt vé"""
        
        return {
            "response": f"🤔 Bạn có muốn đặt vé máy bay không?\n\nNếu có, hãy nói 'đặt vé này' hoặc 'tôi muốn đặt vé'.",
            "suggestions": ["🎯 Đặt vé này", "🔍 Xem thêm chuyến bay", "❌ Không đặt"],
            "context": {
                "agent_type": "booking_confirmation"
            }
        }
    
    async def _handle_booking_flow(self, user_id: str, message: str, booking_session: Dict) -> Dict[str, Any]:
        """Xử lý các bước trong booking flow"""
        
        session_id = booking_session.get('session_id')
        current_step = booking_session.get('step')
        
        if not session_id or not current_step:
            return {
                "response": "😅 Session không hợp lệ. Vui lòng bắt đầu lại.",
                "suggestions": ["🔄 Bắt đầu lại", "🆘 Hỗ trợ"]
            }
        
        if current_step == 'collect_phone':
            # Xử lý input số điện thoại
            result = self.booking_intent_agent.process_phone_input(session_id, message)
            
            if result['success']:
                # Cập nhật step an toàn
                self._safe_update_booking_context(user_id, {'step': 'confirm_user_info'})
                
                suggestions = ["✅ Đúng", "✏️ Sửa thông tin"] if result.get('needs_confirmation') else ["📝 Nhập thông tin"]
                
                return {
                    "response": result['message'],
                    "suggestions": suggestions,
                    "context": {
                        "agent_type": "booking_process",
                        "step": "confirm_user_info",
                        "user_type": result.get('user_type')
                    }
                }
            else:
                return {
                    "response": result['message'],
                    "suggestions": ["📱 Nhập SĐT khác", "❌ Hủy đặt vé"]
                }
        
        elif current_step == 'confirm_user_info':
            # Xử lý xác nhận thông tin
            result = self.booking_intent_agent.process_user_confirmation(session_id, message)
            
            if result['success']:
                # Cập nhật step an toàn
                self._safe_update_booking_context(user_id, {'step': 'collect_additional_info'})
                
                return {
                    "response": result['message'],
                    "suggestions": ["📝 Nhập CCCD & SMS"],
                    "context": {
                        "agent_type": "booking_process",
                        "step": "collect_additional_info"
                    }
                }
            else:
                return {
                    "response": result['message'],
                    "suggestions": ["✅ Đúng", "✏️ Sửa"]
                }
        
        elif current_step == 'collect_additional_info':
            # Xử lý CCCD và SMS
            result = self.booking_intent_agent.process_additional_info(session_id, message)
            
            if result['success']:
                # Cập nhật step an toàn
                self._safe_update_booking_context(user_id, {'step': 'verify_sms'})
                
                return {
                    "response": result['message'],
                    "suggestions": ["🔢 Nhập mã SMS"],
                    "context": {
                        "agent_type": "booking_process",
                        "step": "verify_sms"
                    }
                }
            else:
                return {
                    "response": result['message'],
                    "suggestions": ["📝 Nhập lại CCCD & SMS"]
                }
        
        elif current_step == 'verify_sms':
            # Xử lý mã SMS
            result = self.booking_intent_agent.process_sms_verification(session_id, message)
            
            if result['success']:
                # Hoàn tất booking - lưu thông tin đầy đủ vào context
                session_context = self.context_storage.load_context(user_id) or {}
                flight_info = booking_session.get('flight_info', {})
                
                # Lấy thông tin chuyến bay từ nhiều nguồn
                from_city = None
                to_city = None
                flight_details = {}
                
                # Ưu tiên từ last_search_result
                last_search = session_context.get('last_search_result', {})
                if last_search and 'data' in last_search and 'flights' in last_search['data']:
                    flights = last_search['data']['flights']
                    if flights:
                        selected_flight = flights[0]
                        from_city = selected_flight.get('from_city', selected_flight.get('origin'))
                        to_city = selected_flight.get('to_city', selected_flight.get('destination'))
                        flight_details = {
                            'flight_id': selected_flight.get('flight_id'),
                            'airline': selected_flight.get('airline'),
                            'price': selected_flight.get('price'),
                            'time': selected_flight.get('time'),
                            'date': selected_flight.get('date'),
                            'route': selected_flight.get('route')
                        }
                
                # Fallback từ locations hoặc flight_info
                if not from_city or not to_city:
                    locations = session_context.get('locations', {})
                    from_city = from_city or flight_info.get('from_city') or locations.get('from') or 'Ho Chi Minh City'
                    to_city = to_city or flight_info.get('to_city') or locations.get('to') or 'Hanoi'
                
                # Lưu thông tin booking hoàn chỉnh vào context
                booking_completed_info = {
                    'booking_id': result.get('confirmation_code'),
                    'flight_details': flight_details,
                    'travel_info': {
                        'from_city': from_city,
                        'to_city': to_city,
                        'destination': to_city,
                        'origin': from_city
                    },
                    'booking_date': datetime.now().isoformat(),
                    'status': 'completed'
                }
                
                # Cập nhật session context một cách an toàn - không ghi đè context hiện có
                current_context = self.context_storage.load_context(user_id) or {}
                
                # Chỉ thêm thông tin booking mới, không xóa context cũ
                current_context.update({
                    'completed_booking': booking_completed_info,
                    'current_destination': to_city,
                    'current_origin': from_city
                })
                
                # Đảm bảo không mất thông tin locations và last_search_result
                if 'locations' not in current_context and session_context.get('locations'):
                    current_context['locations'] = session_context['locations']
                if 'last_search_result' not in current_context and session_context.get('last_search_result'):
                    current_context['last_search_result'] = session_context['last_search_result']
                
                self.context_storage.save_context(user_id, current_context)
                
                # Xác định điểm đến chính (nơi cần dịch vụ)
                destination = to_city
                
                # Phân tích loại chuyến đi để đề xuất phù hợp
                trip_context = self._analyze_trip_context(from_city, to_city, flight_info)
                
                # Tạo booking data với context đầy đủ
                booking_data = {
                    "service_type": "flight",
                    "booking_details": {
                        "flight_details": {
                            "from_city": from_city,
                            "to_city": to_city,
                            "flight_id": flight_info.get('flight_id') or result.get('confirmation_code', 'VJ123'),
                            "price": flight_info.get('price', 1500000)
                        }
                    },
                    "trip_context": trip_context
                }
                
                # Lấy gợi ý Sovico services
                upsell_result = self.upsell_agent.get_travel_services_suggestions(booking_data)
                
                # Xóa booking session nhưng giữ thông tin booking đã hoàn thành
                self._safe_remove_booking_context(user_id)
                
                # Tạo response với upselling
                response = result['message']
                if upsell_result.get('message'):
                    response += f"\n\n{upsell_result['message']}"
                
                # Tạo suggestions từ Sovico services linh hoạt
                upsell_suggestions = []
                services = upsell_result.get('services', [])
                
                # Tạo suggestions thông minh dựa trên context chuyến bay
                upsell_suggestions = self._create_contextual_upsell_suggestions(
                    services, from_city, to_city, trip_context
                )
                
                return {
                    "response": response,
                    "suggestions": upsell_suggestions,
                    "context": {
                        "agent_type": "booking_completed_with_upselling",
                        "confirmation_code": result.get('confirmation_code'),
                        "sovico_services": services,
                        "destination": to_city,
                        "origin": from_city,
                        "trip_context": trip_context,
                        "booking_info": booking_completed_info,
                        "session_context": session_context
                    }
                }
            else:
                return {
                    "response": result['message'],
                    "suggestions": ["🔢 Nhập lại mã", "📱 Gửi lại SMS"]
                }
        
        # Fallback
        return {
            "response": "😅 Có lỗi trong quy trình đặt vé. Vui lòng bắt đầu lại.",
            "suggestions": ["🔄 Bắt đầu lại", "🆘 Hỗ trợ"]
        }
    
    def _analyze_trip_context(self, from_city: str, to_city: str, flight_info: Dict) -> Dict[str, Any]:
        """Phân tích context chuyến đi để đề xuất dịch vụ phù hợp"""
        
        # Chuẩn hóa tên thành phố
        from_normalized = from_city.lower().replace(' ', '')
        to_normalized = to_city.lower().replace(' ', '')
        
        # Xác định loại chuyến đi
        trip_type = "domestic"  # Mặc định trong nước
        
        # Xác định mục đích chuyến đi
        purpose = "leisure"  # Mặc định du lịch
        
        # Phân tích thời gian (nếu có)
        time_context = "flexible"  # Mặc định linh hoạt
        
        # Xác định đặc điểm điểm đến
        destination_type = "city"
        if "danang" in to_normalized or "đànẵng" in to_normalized:
            destination_type = "beach_city"
        elif "hanoi" in to_normalized or "hànội" in to_normalized:
            destination_type = "cultural_city"
        elif "hochiminh" in to_normalized or "saigon" in to_normalized or "hcm" in to_normalized:
            destination_type = "business_city"
        
        return {
            "trip_type": trip_type,
            "purpose": purpose,
            "time_context": time_context,
            "destination_type": destination_type,
            "from_normalized": from_normalized,
            "to_normalized": to_normalized
        }
    
    def _create_contextual_upsell_suggestions(self, services: List[Dict], from_city: str, to_city: str, trip_context: Dict) -> List[str]:
        """Tạo suggestions thông minh dựa trên context chuyến bay"""
        
        suggestions = []
        destination_type = trip_context.get("destination_type", "city")
        
        # Ưu tiên dịch vụ theo loại điểm đến
        priority_services = []
        
        if destination_type == "beach_city":
            priority_services = ["hotel", "tour", "transfer", "insurance"]
        elif destination_type == "cultural_city":
            priority_services = ["tour", "hotel", "transfer", "insurance"]
        elif destination_type == "business_city":
            priority_services = ["transfer", "hotel", "tour", "insurance"]
        else:
            priority_services = ["hotel", "transfer", "tour", "insurance"]
        
        # Tạo suggestions theo thứ tự ưu tiên
        services_by_type = {service["type"]: service for service in services}
        
        for service_type in priority_services:
            if service_type in services_by_type:
                service = services_by_type[service_type]
                suggestion = self._format_service_suggestion(service, to_city, destination_type)
                if suggestion:
                    suggestions.append(suggestion)
            
            if len(suggestions) >= 4:  # Giới hạn 4 suggestions
                break
        
        # Fallback nếu không có services
        if not suggestions:
            suggestions = self._get_fallback_suggestions(to_city, destination_type)
        
        return suggestions
    
    def _format_service_suggestion(self, service: Dict, destination: str, destination_type: str) -> str:
        """Format suggestion cho từng loại dịch vụ"""
        
        service_type = service.get("type", "")
        service_name = service.get("name", "")
        
        if service_type == "hotel":
            if destination_type == "beach_city":
                return f"🏨 Resort {destination}"
            else:
                short_name = service_name.replace('Hotel', '').replace('Resort', '').strip()[:12]
                return f"🏨 {short_name}..."
        
        elif service_type == "transfer":
            return f"🚗 Xe đón {destination}"
        
        elif service_type == "tour":
            if destination_type == "cultural_city":
                return f"🎯 Tour {destination}"
            elif destination_type == "beach_city":
                return f"🎯 Tour biển {destination}"
            else:
                short_tour = service_name.replace('Tour', '').strip()[:12]
                return f"🎯 {short_tour}..."
        
        elif service_type == "insurance":
            return "🛡️ Bảo hiểm du lịch"
        
        return None
    
    def _get_fallback_suggestions(self, destination: str, destination_type: str) -> List[str]:
        """Fallback suggestions khi không có services từ UpsellAgent"""
        
        if destination_type == "beach_city":
            return [
                f"🏨 Resort {destination}",
                f"🎯 Tour biển {destination}", 
                f"🚗 Xe đón {destination}",
                "🛡️ Bảo hiểm"
            ]
        elif destination_type == "cultural_city":
            return [
                f"🎯 Tour {destination}",
                f"🏨 Khách sạn {destination}",
                f"🚗 Xe đón {destination}", 
                "🛡️ Bảo hiểm"
            ]
        else:
            return [
                f"🏨 Khách sạn {destination}",
                f"🚗 Xe đón {destination}",
                f"🎯 Tour {destination}",
                "🛡️ Bảo hiểm"
            ]


# Fallback orchestrator nếu không có LLM key
class FallbackOrchestrator:
    """Fallback khi không có LLM API key"""
    
    def __init__(self):
        from agents.orchestrator import BookingOrchestrator
        self.custom_orchestrator = BookingOrchestrator()
        self.provider = "custom"
    
    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Fallback to custom orchestrator"""
        result = await self.custom_orchestrator.process_message(user_id, message)
        result["context"]["agent_type"] = "custom_fallback"
        result["context"]["llm_provider"] = self.provider
        return result