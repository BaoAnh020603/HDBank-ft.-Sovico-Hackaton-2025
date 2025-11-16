from abc import ABC, abstractmethod
from typing import Dict, Any
from models.schemas import AgentRequest, AgentResponse, ConversationContext

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
    
    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process agent request and return response"""
        pass
    
    def validate_input(self, slots: Dict[str, Any], required_slots: list) -> bool:
        """Validate if required slots are present"""
        return all(slot in slots for slot in required_slots)
    
    def create_response(self, success: bool, data: Dict[str, Any], message: str = "") -> AgentResponse:
        """Create standardized agent response"""
        return AgentResponse(
            success=success,
            data=data,
            message=message
        )