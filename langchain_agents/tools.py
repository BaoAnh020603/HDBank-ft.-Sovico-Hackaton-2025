from langchain.tools import BaseTool
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import json

# Tool để tích hợp với custom agents
class FlightSearchTool(BaseTool):
    name: str = "flight_search"
    description: str = "Tìm kiếm chuyến bay từ điểm A đến điểm B vào ngày cụ thể"
    
    def _run(self, from_city: str, to_city: str, date: str) -> str:
        """Gọi custom Search Agent"""
        from agents.search_agent import SearchAgent
        from models.schemas import AgentRequest, ConversationContext
        
        user_input = f"Tìm chuyến bay từ {from_city} đến {to_city} ngày {date}"
        context = ConversationContext(user_id="langchain_tool")
        
        agent = SearchAgent()
        request = AgentRequest(
            intent="flight_search",
            user_input=user_input,
            slots={"from_city": from_city, "to_city": to_city, "date": date},
            context=context
        )
        
        # Chạy sync version
        import asyncio
        result = asyncio.run(agent.process(request))
        
        if result.success:
            flights = result.data.get("flights", [])
            return json.dumps({
                "status": "success",
                "flights": flights[:3],  # Top 3 flights
                "message": f"Tìm thấy {len(flights)} chuyến bay"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "status": "error", 
                "message": result.message
            }, ensure_ascii=False)

class PriceCheckTool(BaseTool):
    name: str = "price_check"
    description: str = "Kiểm tra giá vé máy bay rẻ nhất cho route cụ thể"
    
    def _run(self, from_city: str, to_city: str, date: str = "") -> str:
        """Gọi custom Price Agent với intelligent reasoning"""
        from agents.price_agent import PriceAgent
        from models.schemas import AgentRequest, ConversationContext
        
        # Tạo user input tự nhiên cho PriceAgent
        user_input = f"Kiểm tra giá vé rẻ nhất từ {from_city} đến {to_city}"
        if date:
            user_input += f" ngày {date}"
        
        # Tạo context đúng schema
        context = ConversationContext(
            user_id="langchain_tool",
            slots={"tool_call": True, "from_city": from_city, "to_city": to_city, "date": date}
        )
        
        agent = PriceAgent()
        request = AgentRequest(
            intent="price_check",
            user_input=user_input,
            slots={"from_city": from_city, "to_city": to_city, "date": date},
            context=context
        )
        
        import asyncio
        result = asyncio.run(agent.process(request))
        
        if result.success:
            data = result.data
            if data.get("type") == "cheapest" and data.get("flight"):
                flight = data["flight"]
                return json.dumps({
                    "status": "success",
                    "best_price": flight.get("price"),
                    "flight_id": flight.get("flight_id"),
                    "airline": flight.get("airline"),
                    "time": flight.get("time"),
                    "message": result.message
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "status": "success",
                    "data": data,
                    "message": result.message
                }, ensure_ascii=False)
        else:
            return json.dumps({
                "status": "error",
                "message": result.message
            }, ensure_ascii=False)

class BookingTool(BaseTool):
    name: str = "booking"
    description: str = "Đặt vé máy bay với flight_id cụ thể"
    
    def _run(self, flight_id: str, user_context: str = "{}") -> str:
        """Gọi custom Booking Agent"""
        from agents.booking_agent import BookingAgent
        from models.schemas import AgentRequest, ConversationContext
        
        # Parse context
        try:
            context_data = json.loads(user_context)
        except:
            context_data = {}
        
        user_input = f"Đặt vé chuyến bay {flight_id}"
        context = ConversationContext(
            user_id="langchain_tool",
            slots=context_data
        )
        
        agent = BookingAgent()
        request = AgentRequest(
            intent="booking",
            user_input=user_input,
            slots={"flight_id": flight_id},
            context=context
        )
        
        import asyncio
        result = asyncio.run(agent.process(request))
        
        if result.success:
            return json.dumps({
                "status": "success",
                "booking_id": result.data.get("booking_id"),
                "payment_code": result.data.get("payment_code"),
                "total_amount": result.data.get("total_amount"),
                "deadline": result.data.get("deadline")
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "status": "error",
                "message": result.message
            }, ensure_ascii=False)

# Tạo danh sách tools
def get_booking_tools():
    return [
        FlightSearchTool(),
        PriceCheckTool(), 
        BookingTool()
    ]