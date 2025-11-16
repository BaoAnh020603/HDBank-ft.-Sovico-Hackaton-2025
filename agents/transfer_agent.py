from typing import Dict, Any
from .base_agent import BaseAgent
from models.schemas import AgentRequest, AgentResponse, TransferContext, TransferInfo
from data.mock_data import transfer_generator

class TransferAgent(BaseAgent):
    """Agent for transfer booking and management"""
    
    def __init__(self):
        super().__init__("TransferAgent")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process transfer request"""
        slots = request.slots
        context = request.context
        intent = request.intent
        
        if intent == "transfer_search":
            return await self._search_transfers(slots, context)
        elif intent == "transfer_booking":
            return await self._book_transfer(slots, context)
        else:
            return self.create_response(
                success=False,
                data={},
                message=f"Transfer intent {intent} not supported"
            )
    
    async def _search_transfers(self, slots: Dict[str, Any], context=None) -> AgentResponse:
        """Search transfers and save to context"""
        city = slots.get("city")
        pickup_location = slots.get("pickup_location")
        drop_location = slots.get("drop_location")
        pickup_time = slots.get("pickup_time")
        passengers = slots.get("passengers", 2)
        vehicle_type = slots.get("vehicle_type")
        
        # Auto-detect city from flight context if not provided
        if not city and context and context.flight_context:
            if context.flight_context.search_results:
                # Use destination city from flight
                city = context.flight_context.search_results[0].to_city
        
        if not city:
            return self.create_response(
                success=True,
                data={"need_info": "city"},
                message="🚗 Bạn cần xe đưa đón ở thành phố nào ạ?"
            )
        
        # Get transfers from mock data
        transfers = transfer_generator.generate_transfers(city)
        
        # Filter by vehicle type if specified
        if vehicle_type:
            transfers = [t for t in transfers if vehicle_type.lower() in t["vehicle"].lower()]
        
        if not transfers:
            return self.create_response(
                success=False,
                data={"transfers": []},
                message=f"😔 Không tìm thấy dịch vụ xe đưa đón ở {city}. Bạn thử thành phố khác nhé!"
            )
        
        # Update session context
        if context:
            if not context.transfer_context:
                context.transfer_context = TransferContext()
            
            # Save search criteria
            context.transfer_context.search_criteria = {
                "city": city,
                "pickup_location": pickup_location,
                "drop_location": drop_location,
                "pickup_time": pickup_time,
                "passengers": passengers,
                "vehicle_type": vehicle_type
            }
            
            # Convert to TransferInfo objects
            transfer_infos = []
            for transfer in transfers:
                transfer_info = TransferInfo(
                    service_id=transfer["service_id"],
                    type=transfer["type"],
                    from_location=transfer["from_location"],
                    to_location=transfer["to_location"],
                    price=transfer["price"],
                    vehicle=transfer["vehicle"],
                    pickup_time=pickup_time,
                    passengers=passengers
                )
                transfer_infos.append(transfer_info)
            
            context.transfer_context.search_results = transfer_infos
            print(f"DEBUG: Saved {len(transfer_infos)} transfers to session context")
        
        return self.create_response(
            success=True,
            data={"transfers": transfers},
            message=f"🚗 Tìm thấy {len(transfers)} dịch vụ xe đưa đón ở {city}"
        )
    
    async def _book_transfer(self, slots: Dict[str, Any], context=None) -> AgentResponse:
        """Book selected transfer"""
        transfer_id = slots.get("transfer_id")
        
        if not transfer_id and context and context.transfer_context:
            # Auto-select first transfer if not specified
            if context.transfer_context.search_results:
                transfer_id = context.transfer_context.search_results[0].service_id
        
        if not transfer_id:
            return self.create_response(
                success=False,
                data={},
                message="🚗 Bạn chưa chọn dịch vụ xe nào. Hãy tìm xe trước nhé!"
            )
        
        # Find transfer in context
        selected_transfer = None
        if context and context.transfer_context:
            for transfer in context.transfer_context.search_results:
                if transfer.service_id == transfer_id:
                    selected_transfer = transfer
                    break
        
        if not selected_transfer:
            return self.create_response(
                success=False,
                data={},
                message="🚗 Không tìm thấy dịch vụ xe đã chọn. Bạn thử tìm lại nhé!"
            )
        
        # Generate booking
        import uuid
        from datetime import datetime, timedelta
        
        booking_id = f"TB{uuid.uuid4().hex[:6].upper()}"
        payment_code = f"PAY{uuid.uuid4().hex[:8].upper()}"
        deadline = (datetime.now() + timedelta(hours=2)).strftime("%H:%M %d/%m/%Y")
        
        booking_data = {
            "booking_id": booking_id,
            "payment_code": payment_code,
            "transfer_details": {
                "type": selected_transfer.type,
                "from_location": selected_transfer.from_location,
                "to_location": selected_transfer.to_location,
                "vehicle": selected_transfer.vehicle,
                "pickup_time": selected_transfer.pickup_time,
                "passengers": selected_transfer.passengers
            },
            "total_amount": selected_transfer.price,
            "deadline": deadline,
            "status": "pending_payment"
        }
        
        # Update context with booking
        if context:
            if not context.transfer_context:
                context.transfer_context = TransferContext()
            context.transfer_context.selected_transfers.append(transfer_id)
            context.booking_state["transfer_booking"] = booking_data
        
        return self.create_response(
            success=True,
            data=booking_data,
            message=f"🎉 Đặt xe thành công! Mã booking: {booking_id}"
        )