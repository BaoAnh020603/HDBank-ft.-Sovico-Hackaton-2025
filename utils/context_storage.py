import json
import os
from typing import Dict, Any
from datetime import datetime, timedelta

class ContextStorage:
    """Simple file-based context storage"""
    
    def __init__(self, storage_dir: str = "data/contexts"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_context(self, user_id: str, context: Dict[str, Any]):
        """Save user context to file"""
        context['last_updated'] = datetime.now().isoformat()
        file_path = os.path.join(self.storage_dir, f"{user_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=2)
    
    def load_context(self, user_id: str) -> Dict[str, Any]:
        """Load user context from file"""
        file_path = os.path.join(self.storage_dir, f"{user_id}.json")
        
        if not os.path.exists(file_path):
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                context = json.load(f)
            
            # Check if context is expired (24 hours)
            if 'last_updated' in context:
                last_updated = datetime.fromisoformat(context['last_updated'])
                if datetime.now() - last_updated > timedelta(hours=24):
                    return {}
            
            return context
        except:
            return {}
    
    def clear_context(self, user_id: str):
        """Clear user context"""
        file_path = os.path.join(self.storage_dir, f"{user_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)

# Global instance
context_storage = ContextStorage()