from typing import Dict, Any
from .base_agent import BaseAgent
from models.schemas import AgentRequest, AgentResponse, HotelContext, HotelInfo
from data.mock_data import hotel_generator

class HotelAgent(BaseAgent):
    """Agent for hotel booking and management"""
    
    def __init__(self):
        super().__init__("HotelAgent")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process hotel request"""
        slots = request.slots
        context = request.context
        intent = request.intent
        
        if intent == "hotel_search":
            return await self._search_hotels(slots, context)
        elif intent == "hotel_booking":
            return await self._book_hotel(slots, context)
        else:
            return self.create_response(
                success=False,
                data={},
                message=f"Hotel intent {intent} not supported"
            )
    
    async def _search_hotels(self, slots: Dict[str, Any], context=None) -> AgentResponse:
        """Search hotels and save to context"""
        city = slots.get("city")
        check_in = slots.get("check_in")
        check_out = slots.get("check_out")
        guests = slots.get("guests", 2)
        rating_min = slots.get("rating_min")
        price_max = slots.get("price_max")
        
        if not city:
            return self.create_response(
                success=True,
                data={"need_info": "city"},
                message="🏨 Bạn muốn tìm khách sạn ở thành phố nào ạ?"
            )
        
        # Get hotels from mock data
        hotels = hotel_generator.generate_hotels(city, check_in, 1)
        
        # Apply filters
        if rating_min:
            hotels = [h for h in hotels if h["rating"] >= rating_min]
        if price_max:
            hotels = [h for h in hotels if h["price_per_night"] <= price_max]
        
        if not hotels:
            return self.create_response(
                success=False,
                data={"hotels": []},
                message=f"😔 Không tìm thấy khách sạn phù hợp ở {city}. Bạn thử tiêu chí khác nhé!"
            )
        
        # Update session context
        if context:
            if not context.hotel_context:
                context.hotel_context = HotelContext()
            
            # Save search criteria
            context.hotel_context.search_criteria = {
                "city": city,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "rating_min": rating_min,
                "price_max": price_max
            }
            
            # Convert to HotelInfo objects
            hotel_infos = []
            for hotel in hotels:
                hotel_info = HotelInfo(
                    service_id=hotel["service_id"],
                    name=hotel["name"],
                    location=hotel["location"],
                    rating=hotel["rating"],
                    price_per_night=hotel["price_per_night"],
                    rooms_left=hotel["rooms_left"],
                    type=hotel["type"],
                    check_in=check_in,
                    check_out=check_out,
                    guests=guests
                )
                hotel_infos.append(hotel_info)
            
            context.hotel_context.search_results = hotel_infos
            print(f"DEBUG: Saved {len(hotel_infos)} hotels to session context")
        
        return self.create_response(
            success=True,
            data={"hotels": hotels},
            message=f"🏨 Tìm thấy {len(hotels)} khách sạn ở {city}"
        )
    
    async def _book_hotel(self, slots: Dict[str, Any], context=None) -> AgentResponse:
        """Book selected hotel"""
        hotel_id = slots.get("hotel_id")
        
        if not hotel_id and context and context.hotel_context:
            # Auto-select first hotel if not specified
            if context.hotel_context.search_results:
                hotel_id = context.hotel_context.search_results[0].service_id
        
        if not hotel_id:
            return self.create_response(
                success=False,
                data={},
                message="🏨 Bạn chưa chọn khách sạn nào. Hãy tìm khách sạn trước nhé!"
            )
        
        # Find hotel in context
        selected_hotel = None
        if context and context.hotel_context:
            for hotel in context.hotel_context.search_results:
                if hotel.service_id == hotel_id:
                    selected_hotel = hotel
                    break
        
        if not selected_hotel:
            return self.create_response(
                success=False,
                data={},
                message="🏨 Không tìm thấy khách sạn đã chọn. Bạn thử tìm lại nhé!"
            )
        
        # Generate booking
        import uuid
        from datetime import datetime, timedelta
        
        booking_id = f"HB{uuid.uuid4().hex[:6].upper()}"
        payment_code = f"PAY{uuid.uuid4().hex[:8].upper()}"
        deadline = (datetime.now() + timedelta(hours=2)).strftime("%H:%M %d/%m/%Y")
        
        booking_data = {
            "booking_id": booking_id,
            "payment_code": payment_code,
            "hotel_details": {
                "name": selected_hotel.name,
                "location": selected_hotel.location,
                "rating": selected_hotel.rating,
                "check_in": selected_hotel.check_in,
                "check_out": selected_hotel.check_out,
                "guests": selected_hotel.guests
            },
            "total_amount": selected_hotel.price_per_night * (selected_hotel.nights or 1),
            "deadline": deadline,
            "status": "pending_payment"
        }
        
        # Update context with booking
        if context:
            if not context.hotel_context:
                context.hotel_context = HotelContext()
            context.hotel_context.selected_hotels.append(hotel_id)
            context.booking_state["hotel_booking"] = booking_data
        
        return self.create_response(
            success=True,
            data=booking_data,
            message=f"🎉 Đặt khách sạn thành công! Mã booking: {booking_id}"
        )