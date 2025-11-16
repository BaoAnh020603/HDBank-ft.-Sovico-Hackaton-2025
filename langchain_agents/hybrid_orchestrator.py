from typing import Dict, Any
import os
from .smart_orchestrator import SmartBookingOrchestrator, FallbackOrchestrator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HybridOrchestrator:
    """Hybrid orchestrator: LangChain + Custom Agents"""
    
    def __init__(self):
        # Check available API keys
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.provider = os.getenv("LLM_PROVIDER", "auto")
        
        # Initialize orchestrator with priority: Gemini > OpenAI > Custom
        if self.google_key or self.openai_key:
            try:
                self.orchestrator = SmartBookingOrchestrator(provider=self.provider)
                self.mode = "langchain"
                self.llm_provider = getattr(self.orchestrator, 'provider', 'unknown')
                print(f"🧠 Initialized LangChain with {self.llm_provider.upper()}")
            except Exception as e:
                print(f"⚠️ LangChain init failed: {e}")
                self.orchestrator = FallbackOrchestrator()
                self.mode = "fallback"
                self.llm_provider = "custom"
        else:
            self.orchestrator = FallbackOrchestrator()
            self.mode = "custom"
            self.llm_provider = "custom"
            print("🔧 Using Custom Orchestrator (no LLM keys)")
    
    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process message với hybrid approach"""
        
        # Thêm thông tin về mode vào response
        result = await self.orchestrator.process_message(user_id, message)
        
        # Đảm bảo có context key
        if "context" not in result:
            result["context"] = {}
        
        result["context"]["orchestrator_mode"] = self.mode
        result["context"]["llm_provider"] = self.llm_provider
        
        # Enhance response với provider-specific icons
        if self.mode == "langchain":
            if self.llm_provider == "gemini":
                result["response"] = f"🔥 {result['response']}"
            elif self.llm_provider == "openai":
                result["response"] = f"🧠 {result['response']}"
        else:
            result["response"] = f"🔧 {result['response']}"
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Trả về trạng thái của orchestrator"""
        return {
            "mode": self.mode,
            "llm_provider": self.llm_provider,
            "has_openai": bool(self.openai_key),
            "has_gemini": bool(self.google_key),
            "preferred_provider": self.provider,
            "orchestrator_type": type(self.orchestrator).__name__
        }