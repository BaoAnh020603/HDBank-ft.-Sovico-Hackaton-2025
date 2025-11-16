from typing import Dict, Any, List
from .base_agent import BaseAgent
from models.schemas import AgentRequest, AgentResponse, ComboContext, ComboResponse, ComboItem
try:
    from data.mock_data_loader import get_flights_by_route
    from data.mock_data import hotel_generator, transfer_generator, combo_generator
except ImportError:
    from data.mock_data import combo_generator, hotel_generator, transfer_generator, get_flights_by_route

class ComboAgent(BaseAgent):
    """Agent for combo services and packages with session context"""
    
    def __init__(self):
        super().__init__("ComboAgent")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process combo service request"""
        slots = request.slots
        context = request.context
        intent = request.intent
        
        if intent == "combo_search":
            return await self._search_combos(slots, context)
        elif intent == "combo_booking":
            return await self._book_combo(slots, context)
        else:
            # Legacy support - check for existing flight context
            if context and context.flight_context and context.flight_context.search_results:
                # Use first flight result to create combo
                flight_info = context.flight_context.search_results[0]
                flight_dict = {
                    "service_id": flight_info.service_id,
                    "flight_id": flight_info.flight_id,
                    "airline": flight_info.airline,
                    "to_city": flight_info.to_city,
                    "price": flight_info.price
                }
                return await self._create_personalized_combo(flight_dict, slots, context)
            else:
                return await self._show_available_combos(slots, context)
    

    
    async def _search_combos(self, slots: Dict[str, Any], context=None) -> AgentResponse:
        """Search for combo packages and save to context"""
        destination = slots.get("destination")
        
        # Auto-detect destination from flight context
        if not destination and context and context.flight_context:
            if context.flight_context.search_results:
                destination = context.flight_context.search_results[0].to_city
        
        if not destination:
            return self.create_response(
                success=True,
                data={"need_info": "destination"},
                message="🎁 Bạn muốn xem combo du lịch đến đâu ạ?"
            )
        
        # Generate combos based on available services
        combos = []
        
        # If flight context exists, create personalized combos
        if context and context.flight_context and context.flight_context.search_results:
            for flight_info in context.flight_context.search_results[:2]:  # Top 2 flights
                flight_dict = {
                    "service_id": flight_info.service_id,
                    "flight_id": flight_info.flight_id,
                    "airline": flight_info.airline,
                    "to_city": flight_info.to_city,
                    "price": flight_info.price
                }
                combo = combo_generator.generate_combo(flight_dict, destination)
                if combo:
                    combos.append(combo)
        
        # Update session context
        if context:
            if not context.combo_context:
                context.combo_context = ComboContext()
            
            # Convert to ComboResponse objects
            combo_responses = []
            for combo in combos:
                combo_items = []
                for item in combo["items"]:
                    combo_item = ComboItem(
                        type=item["type"],
                        service_id=item["service_id"],
                        name=item["name"],
                        price=item["price"]
                    )
                    combo_items.append(combo_item)
                
                combo_response = ComboResponse(
                    combo_id=combo["combo_id"],
                    name=combo["name"],
                    items=combo_items,
                    total_price=combo["total_price"],
                    discount=combo["discount"],
                    final_price=combo["final_price"]
                )
                combo_responses.append(combo_response)
            
            context.combo_context.available_combos = combo_responses
            print(f"DEBUG: Saved {len(combo_responses)} combos to session context")
        
        if not combos:
            return self.create_response(
                success=False,
                data={"combos": []},
                message=f"😔 Chưa có combo phù hợp cho {destination}. Hãy tìm vé bay trước nhé!"
            )
        
        return self.create_response(
            success=True,
            data={"combos": combos},
            message=f"🎁 Tìm thấy {len(combos)} combo du lịch cho {destination}"
        )
    
    async def _book_combo(self, slots: Dict[str, Any], context=None) -> AgentResponse:
        """Book selected combo"""
        combo_id = slots.get("combo_id")
        
        if not combo_id and context and context.combo_context:
            # Auto-select first combo if not specified
            if context.combo_context.available_combos:
                combo_id = context.combo_context.available_combos[0].combo_id
        
        if not combo_id:
            return self.create_response(
                success=False,
                data={},
                message="🎁 Bạn chưa chọn combo nào. Hãy xem combo trước nhé!"
            )
        
        # Find combo in context
        selected_combo = None
        if context and context.combo_context:
            for combo in context.combo_context.available_combos:
                if combo.combo_id == combo_id:
                    selected_combo = combo
                    break
        
        if not selected_combo:
            return self.create_response(
                success=False,
                data={},
                message="🎁 Không tìm thấy combo đã chọn. Bạn thử tìm lại nhé!"
            )
        
        # Generate booking
        import uuid
        from datetime import datetime, timedelta
        
        booking_id = f"CB{uuid.uuid4().hex[:6].upper()}"
        payment_code = f"PAY{uuid.uuid4().hex[:8].upper()}"
        deadline = (datetime.now() + timedelta(hours=2)).strftime("%H:%M %d/%m/%Y")
        
        booking_data = {
            "booking_id": booking_id,
            "payment_code": payment_code,
            "combo_details": {
                "name": selected_combo.name,
                "items": [item.dict() for item in selected_combo.items],
                "total_price": selected_combo.total_price,
                "discount": selected_combo.discount
            },
            "total_amount": selected_combo.final_price,
            "deadline": deadline,
            "status": "pending_payment"
        }
        
        # Update context with booking
        if context:
            if not context.combo_context:
                context.combo_context = ComboContext()
            context.combo_context.selected_combo = combo_id
            context.booking_state["combo_booking"] = booking_data
        
        return self.create_response(
            success=True,
            data=booking_data,
            message=f"🎉 Đặt combo thành công! Mã booking: {booking_id}"
        )
    
    async def _create_personalized_combo(self, flight: Dict[str, Any], slots: Dict[str, Any], context=None) -> AgentResponse:
        """Create personalized combo based on flight using dynamic generator"""
        destination = flight["to_city"]
        
        # Generate combo động dựa trên chuyến bay
        combo = combo_generator.generate_combo(flight, destination)
        
        if combo:
            # Tạo thêm 1-2 combo khác với các option khác nhau
            combos = [combo]
            
            # Combo chỉ có flight + hotel (không transfer)
            hotels = hotel_generator.generate_hotels(destination, flight.get("date"))
            if len(hotels) > 1:
                alt_hotel = hotels[1] if len(hotels) > 1 else hotels[0]
                alt_combo = {
                    "combo_id": f"CB_ALT_{flight['service_id']}",
                    "name": f"Combo Tiết Kiệm - {flight['airline']} + {alt_hotel['name']}",
                    "items": [
                        {
                            "type": "flight",
                            "service_id": flight["service_id"],
                            "name": f"{flight['airline']} {flight['flight_id']}",
                            "price": flight["price"]
                        },
                        {
                            "type": "hotel",
                            "service_id": alt_hotel["service_id"],
                            "name": alt_hotel["name"],
                            "price": alt_hotel["price_per_night"]
                        }
                    ],
                    "total_price": flight["price"] + alt_hotel["price_per_night"],
                    "discount": int((flight["price"] + alt_hotel["price_per_night"]) * 0.08),
                    "final_price": int((flight["price"] + alt_hotel["price_per_night"]) * 0.92)
                }
                combos.append(alt_combo)
            
            return self.create_response(
                success=True,
                data={"combos": combos},
                message=f"Tạo được {len(combos)} gói combo phù hợp cho chuyến {flight['flight_id']} của bạn!"
            )
        else:
            return self.create_response(
                success=True,
                data={"combos": []},
                message=f"Hiện tại chưa có gói combo cho điểm đến {destination}. Tôi sẽ cập nhật sớm!"
            )
    
    async def _show_available_combos(self, slots: Dict[str, Any], context=None) -> AgentResponse:
        """Show sample combo packages"""
        # Tạo một số combo mẫu
        sample_combos = []
        
        # Combo Hà Nội - Đà Nẵng
        # get_flights_by_route already imported at top
        sample_flights = get_flights_by_route("HAN", "DAD", "2025-01-30")
        if sample_flights:
            combo = combo_generator.generate_combo(sample_flights[0], "DAD")
            if combo:
                sample_combos.append(combo)
        
        if sample_combos:
            return self.create_response(
                success=True,
                data={"combos": sample_combos},
                message=f"Dưới đây là một số gói combo phổ biến. Bạn hãy chọn chuyến bay trước để xem combo phù hợp nhất!"
            )
        else:
            return self.create_response(
                success=True,
                data={"combos": []},
                message="Vui lòng chọn chuyến bay trước, tôi sẽ gợi ý combo phù hợp nhất cho bạn!"
            )