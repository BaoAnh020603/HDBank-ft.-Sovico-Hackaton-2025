from typing import Dict, Any
from datetime import datetime
from utils.nlu import SimpleNLU
from models.schemas import ConversationContext, AgentRequest
from .search_agent import SearchAgent
try:
    from .price_agent import PriceAgent
except Exception as e:
    print(f"Warning: PriceAgent import failed in orchestrator: {e}")
    PriceAgent = None
from .booking_agent import BookingAgent
from .combo_agent import ComboAgent

class BookingOrchestrator:
    """Main orchestrator for managing conversation flow and agents"""
    
    def __init__(self):
        self.nlu = SimpleNLU()
        self.agents = {
            "search": SearchAgent(),
            "price": PriceAgent() if PriceAgent else None, 
            "booking": BookingAgent(),
            "combo": ComboAgent()
        }
        # In-memory context storage (sẽ thay bằng Redis)
        self.contexts = {}
    
    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process user message and return response"""
        
        # 1. Load or create context
        context = self._load_context(user_id)
        
        # 2. NLU processing
        intent, slots = self.nlu.process(message, context.slots)
        
        # 3. Update context
        context.intent = intent
        context.slots.update(slots)
        context.last_updated = datetime.now()
        
        # 4. Route to appropriate agent
        agent_name = self._select_agent(intent)
        agent = self.agents[agent_name]
        
        # 5. Create agent request
        agent_request = AgentRequest(
            intent=intent,
            slots=slots,
            context=context
        )
        
        # 6. Process with agent
        agent_response = await agent.process(agent_request)
        
        # 7. Update context with results
        if agent_response.success:
            self._update_context_with_results(context, intent, agent_response.data)
        
        # 8. Save context
        self._save_context(context)
        
        # 9. Generate natural language response
        response_text = self._generate_vietnamese_response(intent, agent_response, slots)
        
        # 10. Generate suggestions
        suggestions = self._generate_suggestions(intent, agent_response, context)
        
        return {
            "response": response_text,
            "context": {
                "agent_type": "fallback_orchestrator",
                "session_context": context.dict()
            },
            "suggestions": suggestions
        }
    
    def _load_context(self, user_id: str) -> ConversationContext:
        """Load user context from storage"""
        if user_id in self.contexts:
            return self.contexts[user_id]
        else:
            return ConversationContext(user_id=user_id)
    
    def _save_context(self, context: ConversationContext):
        """Save context to storage"""
        self.contexts[context.user_id] = context
    
    def _select_agent(self, intent: str) -> str:
        """Select appropriate agent based on intent"""
        agent_mapping = {
            "flight_search": "search",
            "price_check": "price", 
            "booking": "booking",
            "combo_service": "combo",
            "general": "search"  # Default to search
        }
        return agent_mapping.get(intent, "search")
    
    def _update_context_with_results(self, context: ConversationContext, intent: str, data: Dict[str, Any]):
        """Update context with agent results"""
        if intent == "booking" and "booking_id" in data:
            context.booking_state = data
        elif intent == "flight_search" and "flights" in data:
            context.slots["last_search_results"] = data["flights"]
    
    def _generate_vietnamese_response(self, intent: str, agent_response, slots: Dict[str, Any]) -> str:
        """Generate natural Vietnamese language response"""
        if not agent_response.success:
            return self._vietnamize_error_message(agent_response.message)
        
        data = agent_response.data
        
        if intent == "flight_search":
            flights = data.get("flights", [])
            if flights:
                from_city = self._get_city_name(slots.get("from_city", ""))
                to_city = self._get_city_name(slots.get("to_city", ""))
                
                response = f"🛫 Tìm thấy {len(flights)} chuyến bay từ {from_city} đến {to_city}:\n\n"
                for i, flight in enumerate(flights[:3], 1):
                    response += f"{i}. ✈️ {flight['airline']} {flight['flight_id']}\n"
                    response += f"   ⏰ Khởi hành: {flight['time']} - {flight['date']}\n"
                    response += f"   💰 Giá vé: {flight['price']:,}đ\n"
                    response += f"   🪑 Còn lại: {flight['seats_left']} ghế\n\n"
                
                if len(flights) > 3:
                    response += f"... và {len(flights) - 3} chuyến bay khác\n"
                return response
            else:
                from_city = self._get_city_name(slots.get("from_city", ""))
                to_city = self._get_city_name(slots.get("to_city", ""))
                return f"😔 Rất tiếc, hiện tại không có chuyến bay từ {from_city} đến {to_city}. Bạn có thể thử ngày khác không?"
        
        elif intent == "price_check":
            if "best_price" in data:
                return f"💰 Vé rẻ nhất: {data['best_price']:,}đ\n✈️ Chuyến bay: {data['airline']} {data['flight_id']}\n⏰ Giờ bay: {data['time']}\n🪑 Còn {data['seats_left']} ghế"
            elif "flights" in data:
                flights = data["flights"]
                return f"💰 Khoảng giá vé: {flights[0]['price']:,}đ - {flights[-1]['price']:,}đ\n📊 Có {len(flights)} lựa chọn cho bạn"
        
        elif intent == "booking":
            if "booking_id" in data:
                flight_info = data.get("flight_details", {})
                response = f"🎉 Đặt vé thành công!\n\n"
                response += f"📋 Thông tin booking:\n"
                response += f"🆔 Mã đặt chỗ: {data['booking_id']}\n"
                response += f"💳 Mã thanh toán: {data['payment_code']}\n\n"
                response += f"✈️ Chi tiết chuyến bay:\n"
                response += f"🛫 {flight_info.get('route', '')}\n"
                response += f"📅 {flight_info.get('date', '')} - {flight_info.get('time', '')}\n"
                response += f"🏢 {flight_info.get('airline', '')} {flight_info.get('flight_id', '')}\n\n"
                response += f"💰 Tổng tiền: {data['total_amount']:,}đ\n"
                response += f"⏰ Hạn thanh toán: {data['deadline']}\n\n"
                response += f"📞 Vui lòng thanh toán trước thời hạn để giữ chỗ!"
                return response
        
        elif intent == "combo_service":
            combos = data.get("combos", [])
            if combos:
                response = f"🎁 Có {len(combos)} gói combo hấp dẫn cho bạn:\n\n"
                for i, combo in enumerate(combos[:2], 1):
                    response += f"{i}. 🌟 {combo['name']}\n"
                    
                    # Hiển thị các item trong combo
                    items = combo.get('items', [])
                    for item in items:
                        if item['type'] == 'flight':
                            response += f"   ✈️ Vé máy bay: {item['price']:,}đ\n"
                        elif item['type'] == 'hotel':
                            response += f"   🏨 Khách sạn: {item['price']:,}đ\n"
                        elif item['type'] == 'transfer':
                            response += f"   🚗 Đưa đón: {item['price']:,}đ\n"
                    
                    response += f"   💵 Tổng giá gốc: {combo['total_price']:,}đ\n"
                    response += f"   🎯 Giảm giá: -{combo['discount']:,}đ\n"
                    response += f"   ✨ Giá ưu đãi: {combo['final_price']:,}đ\n\n"
                
                response += f"💡 Tiết kiệm hơn khi đặt combo! Bạn có muốn đặt không?"
                return response
            else:
                return "😊 Hiện tại chưa có gói combo phù hợp. Tôi sẽ thông báo khi có ưu đãi mới!"
        
        return agent_response.message or "✅ Đã xử lý xong yêu cầu của bạn!"
    
    def _get_city_name(self, city_code: str) -> str:
        """Convert city code to Vietnamese name"""
        city_names = {
            "HAN": "Hà Nội",
            "DAD": "Đà Nẵng", 
            "SGN": "TP. Hồ Chí Minh"
        }
        return city_names.get(city_code, city_code)
    
    def _vietnamize_error_message(self, message: str) -> str:
        """Convert error messages to friendly Vietnamese"""
        if "missing_slots" in message.lower():
            return "😊 Bạn có thể cho tôi biết thêm thông tin về điểm đi và điểm đến không?"
        elif "not found" in message.lower():
            return "😔 Không tìm thấy thông tin bạn yêu cầu. Bạn có thể thử cách khác không?"
        elif "not supported" in message.lower():
            return "🔧 Tính năng này đang được phát triển. Tôi sẽ hỗ trợ bạn sớm nhất!"
        return f"😊 {message}"
    
    def _generate_suggestions(self, intent: str, agent_response, context: ConversationContext) -> list:
        """Generate contextual Vietnamese suggestions"""
        suggestions = []
        
        if intent == "flight_search" and agent_response.success:
            data = agent_response.data
            flights = data.get("flights", [])
            if flights:
                suggestions = [
                    "💰 Xem giá vé rẻ nhất",
                    f"✈️ Đặt vé {flights[0]['flight_id']}",
                    "🎁 Tìm gói combo tiết kiệm",
                    "📅 Thay đổi ngày bay"
                ]
        elif intent == "price_check" and agent_response.success:
            suggestions = [
                "🎯 Đặt vé ngay",
                "🔍 Xem thêm chuyến bay",
                "🏨 Thêm khách sạn",
                "📅 Thử ngày khác"
            ]
        elif intent == "booking" and agent_response.success:
            suggestions = [
                "🏨 Thêm khách sạn",
                "🚗 Đặt xe đưa đón", 
                "🎁 Xem gói combo",
                "📋 Xem thông tin booking"
            ]
        elif intent == "combo_service" and agent_response.success:
            suggestions = [
                "✅ Đặt combo này",
                "🔍 Xem combo khác",
                "💰 So sánh giá",
                "📞 Tư vấn thêm"
            ]
        else:
            # Default suggestions
            suggestions = [
                "🛫 Tìm chuyến bay",
                "💰 Kiểm tra giá vé",
                "🎁 Xem gói combo"
            ]
        
        return suggestions