from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import json
from datetime import datetime

app = FastAPI(title="Booking Agent API")

# Basic models
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    context: Dict[str, Any]
    suggestions: list = []

# In-memory context storage (sẽ thay bằng Redis sau)
user_contexts = {}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint"""
    from langchain_agents.hybrid_orchestrator import HybridOrchestrator
    
    orchestrator = HybridOrchestrator()
    result = await orchestrator.process_message(request.user_id, request.message)
    
    return ChatResponse(**result)

@app.get("/")
async def root():
    return {"message": "Booking Agent API is running"}

@app.get("/status")
async def get_status():
    """Get orchestrator status"""
    orchestrator = HybridOrchestrator()
    return orchestrator.get_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)