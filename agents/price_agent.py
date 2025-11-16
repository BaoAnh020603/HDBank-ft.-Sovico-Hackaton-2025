from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from .base_agent import BaseAgent
from models.schemas import AgentRequest, AgentResponse
from data.mock_data_loader import get_cheapest_flight, get_flights_by_route
import json
import os
from dotenv import load_dotenv

load_dotenv()

class PriceAgent(BaseAgent):
    """Agent for price checking and comparison with intelligent reasoning"""
    
    def __init__(self):
        super().__init__("PriceAgent")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        ) if os.getenv("GOOGLE_API_KEY") else None
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process price request with intelligent reasoning"""
        user_input = request.user_input
        context = request.context or {}
        
        if not self.llm:
            return await self._fallback_processing(user_input, context)
        
        try:
            # Step 1: Extract price-related entities
            extracted_info = self._extract_price_entities(user_input)
            
            # Step 2: Reason about price intent
            intent_analysis = self._reason_price_intent(extracted_info)
            
            # Step 3: Execute price search
            price_result = await self._search_prices(extracted_info)
            
            # Step 4: Synthesize response
            all_context = f"""
            User Input: {user_input}
            Extracted Information: {extracted_info}
            Intent Analysis: {intent_analysis}
            Price Result: {price_result}
            """
            
            final_response = self._synthesize_price_response(all_context)
            
            return self.create_response(
                success=True,
                data=self._safe_parse_json(price_result),
                message=final_response
            )
            
        except Exception as e:
            return await self._fallback_processing(user_input, context)
    
    def _extract_price_entities(self, input_text: str) -> str:
        """Extract price-related entities using LLM"""
        if not self.llm:
            return "{}"
        
        prompt = f"""
        Phân tích yêu cầu về giá vé máy bay:
        "{input_text}"
        
        Trả về JSON với các fields:
        - locations: {{from: "", to: ""}}
        - time: {{date: "", flexible: true/false}}
        - price_intent: "check_price"/"compare_prices"/"find_cheapest"/"price_range"
        - budget: {{max_price: "", preferred_range: ""}}
        - passengers: số người
        - intent_signals: [list các từ/cụm từ chỉ ý định về giá]
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except:
            return "{}"
    
    def _reason_price_intent(self, extracted_info: str) -> str:
        """Reason about price-related intent"""
        if not self.llm:
            return "check_price"
        
        prompt = f"""
        Dựa vào thông tin đã trích xuất:
        {extracted_info}
        
        Suy luận về ý định kiểm tra giá:
        - Họ muốn làm gì? (check_single_price/compare_multiple/find_cheapest/price_alert)
        - Mức độ linh hoạt về thời gian?
        - Ngân sách có hạn chế không?
        - Cần so sánh nhiều tùy chọn?
        
        Trả về JSON:
        {{
            "primary_intent": "",
            "flexibility": "high/medium/low",
            "budget_conscious": true/false,
            "comparison_needed": true/false,
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except:
            return '{"primary_intent": "check_price", "confidence": 0.5}'
    
    async def _search_prices(self, search_criteria: str) -> str:
        """Execute price search"""
        try:
            criteria = json.loads(search_criteria)
            
            from_city = criteria.get('locations', {}).get('from', '')
            to_city = criteria.get('locations', {}).get('to', '')
            date = criteria.get('time', {}).get('date', '')
            price_intent = criteria.get('price_intent', 'check_price')
            
            if from_city and to_city:
                if price_intent == 'find_cheapest':
                    cheapest = get_cheapest_flight(from_city, to_city, date)
                    return json.dumps({
                        "success": True,
                        "type": "cheapest",
                        "flight": cheapest
                    })
                else:
                    flights = get_flights_by_route(from_city, to_city, date)
                    sorted_flights = sorted(flights, key=lambda x: x["price"]) if flights else []
                    return json.dumps({
                        "success": True,
                        "type": "comparison",
                        "flights": sorted_flights[:5],
                        "price_range": {
                            "min": sorted_flights[0]["price"] if sorted_flights else 0,
                            "max": sorted_flights[-1]["price"] if sorted_flights else 0
                        }
                    })
            else:
                return json.dumps({
                    "success": False,
                    "error": "Missing location information"
                })
                
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    def _synthesize_price_response(self, all_info: str) -> str:
        """Synthesize final price response"""
        if not self.llm:
            return "Đã kiểm tra giá vé cho bạn."
        
        prompt = f"""
        Bạn là chuyên gia tư vấn giá vé máy bay. Tạo response dựa trên:
        {all_info}
        
        YÊU CẦU RESPONSE:
        1. BẮT ĐẦU bằng việc thể hiện hiểu biết về yêu cầu kiểm tra giá
        2. THÔNG TIN GIÁ:
           - Nếu tìm được giá: hiển thị rõ ràng, so sánh nếu có nhiều tùy chọn
           - Nếu thiếu thông tin: hỏi cụ thể
           - Nếu không tìm thấy: gợi ý thay thế
        3. GỢI Ý THÊM:
           - Tips tiết kiệm
           - Thời điểm tốt để đặt vé
           - Các tùy chọn khác
        4. TONE: Chuyên nghiệp, hữu ích, thân thiện
        
        VÍ DỤ TỐT:
        "Tôi đã kiểm tra giá vé từ Hà Nội đến TP.HCM cho bạn. Giá rẻ nhất hiện tại là 1.200.000đ với VietJet..."
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except:
            return "Tôi đã kiểm tra giá vé cho bạn. Bạn có thể cho thêm thông tin để tôi hỗ trợ tốt hơn không?"
    
    async def _fallback_processing(self, user_input: str, context: Dict[str, Any]) -> AgentResponse:
        """Fallback processing without LLM"""
        basic_info = self._basic_price_extraction(user_input)
        
        if basic_info.get('locations', {}).get('from') and basic_info.get('locations', {}).get('to'):
            response = f"Tôi sẽ kiểm tra giá vé từ {basic_info['locations']['from']} đến {basic_info['locations']['to']} cho bạn."
        elif basic_info.get('price_intent') == 'check_price':
            response = "Tôi có thể giúp bạn kiểm tra giá vé máy bay. Bạn muốn xem giá vé tuyến nào?"
        else:
            response = "Tôi có thể hỗ trợ kiểm tra và so sánh giá vé máy bay. Bạn cần thông tin gì?"
        
        return self.create_response(
            success=True,
            data=basic_info,
            message=response
        )
    
    def _basic_price_extraction(self, text: str) -> Dict[str, Any]:
        """Basic price entity extraction"""
        text_lower = text.lower()
        
        # Detect price intent
        price_intent = "check_price"
        if any(word in text_lower for word in ['so sánh', 'compare']):
            price_intent = "compare_prices"
        elif any(word in text_lower for word in ['rẻ nhất', 'cheapest']):
            price_intent = "find_cheapest"
        
        # Basic location detection
        locations = {}
        location_keywords = {
            'hà nội': 'Hà Nội', 'hn': 'Hà Nội',
            'sài gòn': 'TP.HCM', 'hcm': 'TP.HCM',
            'đà nẵng': 'Đà Nẵng'
        }
        
        found_locations = []
        for keyword, city in location_keywords.items():
            if keyword in text_lower:
                found_locations.append(city)
        
        if len(found_locations) >= 2:
            locations = {'from': found_locations[0], 'to': found_locations[1]}
        
        return {
            'locations': locations,
            'price_intent': price_intent,
            'budget': {}
        }
    
    def _safe_parse_json(self, json_str: str) -> Dict[str, Any]:
        """Safely parse JSON string"""
        try:
            return json.loads(json_str)
        except:
            return {}