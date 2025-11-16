from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import json
import requests
import os

class SovicoServicesAgent:
    """Agent xử lý các dịch vụ của Sovico: khách sạn, xe đưa đón, tour, bảo hiểm"""
    
    def __init__(self, api_key: str = None):
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"), 
            temperature=0, 
            google_api_key=api_key or os.getenv("GOOGLE_API_KEY")
        )
        
        # Mock data các dịch vụ Sovico
        self.services_data = {
            "hotels": [
                {"id": "H001", "name": "Sovico Hotel Saigon", "location": "Q1, HCM", "price": 1200000, "rating": 4.5},
                {"id": "H002", "name": "Sovico Resort Da Nang", "location": "Da Nang", "price": 2500000, "rating": 4.8}
            ],
            "transfers": [
                {"id": "T001", "type": "Airport Transfer", "route": "SGN-City", "price": 300000, "vehicle": "Sedan"},
                {"id": "T002", "type": "City Transfer", "route": "Any", "price": 200000, "vehicle": "SUV"}
            ],
            "tours": [
                {"id": "TR001", "name": "Mekong Delta Tour", "duration": "1 day", "price": 800000, "rating": 4.6},
                {"id": "TR002", "name": "Cu Chi Tunnels", "duration": "Half day", "price": 600000, "rating": 4.4}
            ],
            "insurance": [
                {"id": "I001", "type": "Domestic Travel", "coverage": "50M VND", "price": 150000},
                {"id": "I002", "type": "International", "coverage": "100M VND", "price": 350000}
            ]
        }
        
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Tạo tools cho các dịch vụ"""
        
        def search_hotels(query: str) -> str:
            """Tìm khách sạn"""
            try:
                data = json.loads(query) if query.startswith('{') else {"location": query}
                location = data.get("location", "").lower()
                
                results = []
                for hotel in self.services_data["hotels"]:
                    if not location or location in hotel["location"].lower():
                        results.append(hotel)
                
                return json.dumps({"status": "success", "hotels": results})
            except Exception as e:
                return json.dumps({"status": "error", "message": str(e)})
        
        def search_transfers(query: str) -> str:
            """Tìm dịch vụ xe đưa đón"""
            try:
                data = json.loads(query) if query.startswith('{') else {"type": query}
                transfer_type = data.get("type", "").lower()
                
                results = []
                for transfer in self.services_data["transfers"]:
                    if not transfer_type or transfer_type in transfer["type"].lower():
                        results.append(transfer)
                
                return json.dumps({"status": "success", "transfers": results})
            except Exception as e:
                return json.dumps({"status": "error", "message": str(e)})
        
        def search_tours(query: str) -> str:
            """Tìm tour du lịch"""
            try:
                data = json.loads(query) if query.startswith('{') else {"name": query}
                
                results = self.services_data["tours"]  # Trả về tất cả tours
                return json.dumps({"status": "success", "tours": results})
            except Exception as e:
                return json.dumps({"status": "error", "message": str(e)})
        
        def get_insurance_options(query: str) -> str:
            """Lấy tùy chọn bảo hiểm"""
            try:
                results = self.services_data["insurance"]
                return json.dumps({"status": "success", "insurance": results})
            except Exception as e:
                return json.dumps({"status": "error", "message": str(e)})
        
        def format_service_info(service_data: str) -> str:
            """Format thông tin dịch vụ"""
            try:
                data = json.loads(service_data)
                
                if "hotels" in data:
                    formatted = []
                    for hotel in data["hotels"]:
                        formatted.append(f"🏨 {hotel['name']}\n📍 {hotel['location']}\n💰 {hotel['price']:,} VND/đêm\n⭐ {hotel['rating']}/5")
                    return "\n\n".join(formatted)
                
                elif "transfers" in data:
                    formatted = []
                    for transfer in data["transfers"]:
                        formatted.append(f"🚗 {transfer['type']}\n📍 {transfer['route']}\n💰 {transfer['price']:,} VND\n🚙 {transfer['vehicle']}")
                    return "\n\n".join(formatted)
                
                elif "tours" in data:
                    formatted = []
                    for tour in data["tours"]:
                        formatted.append(f"🎯 {tour['name']}\n⏰ {tour['duration']}\n💰 {tour['price']:,} VND\n⭐ {tour['rating']}/5")
                    return "\n\n".join(formatted)
                
                elif "insurance" in data:
                    formatted = []
                    for ins in data["insurance"]:
                        formatted.append(f"🛡️ {ins['type']}\n💰 {ins['price']:,} VND\n🏥 Bảo hiểm: {ins['coverage']}")
                    return "\n\n".join(formatted)
                
                return "Không có thông tin dịch vụ"
                
            except Exception as e:
                return f"Lỗi format: {str(e)}"
        
        return [
            Tool(name="search_hotels", description="Tìm khách sạn theo địa điểm", func=search_hotels),
            Tool(name="search_transfers", description="Tìm dịch vụ xe đưa đón", func=search_transfers),
            Tool(name="search_tours", description="Tìm tour du lịch", func=search_tours),
            Tool(name="get_insurance_options", description="Lấy tùy chọn bảo hiểm", func=get_insurance_options),
            Tool(name="format_service_info", description="Format thông tin dịch vụ", func=format_service_info)
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Tạo LangChain agent"""
        
        system_prompt = """Bạn là Sovico Services Agent, chuyên tư vấn các dịch vụ của Sovico:
- Khách sạn
- Xe đưa đón sân bay/thành phố  
- Tour du lịch
- Bảo hiểm du lịch

Nhiệm vụ: Tìm kiếm và tư vấn dịch vụ phù hợp với nhu cầu khách hàng.
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # Gemini không support functions agent, dùng ReAct
        from langchain.agents import create_react_agent
        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def get_service_recommendations(self, service_type: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Lấy gợi ý dịch vụ"""
        
        query = f"Tìm {service_type} với yêu cầu: {json.dumps(requirements, ensure_ascii=False)}"
        
        try:
            result = self.agent.invoke({"input": query})
            return {"status": "success", "response": result.get("output", "")}
        except Exception as e:
            return {"status": "error", "message": str(e)}