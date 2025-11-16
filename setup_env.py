#!/usr/bin/env python3
"""
Setup script để tạo .env file với API keys
"""
import os

def setup_environment():
    """Setup environment variables"""
    print("🔧 === SETUP BOOKING AGENT ENVIRONMENT ===\n")
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("📁 File .env đã tồn tại!")
        overwrite = input("Bạn có muốn ghi đè không? (y/N): ").lower()
        if overwrite != 'y':
            print("❌ Hủy setup")
            return
    
    print("🔑 Nhập API keys (Enter để bỏ qua):\n")
    
    # Get API keys
    google_key = input("Google Gemini API Key: ").strip()
    openai_key = input("OpenAI API Key: ").strip()
    
    # Get preferences
    print("\n⚙️ Cấu hình:")
    if google_key and openai_key:
        provider = input("LLM Provider (gemini/openai/auto) [gemini]: ").strip() or "gemini"
    elif google_key:
        provider = "gemini"
        print("→ Sử dụng Gemini (chỉ có Gemini key)")
    elif openai_key:
        provider = "openai"
        print("→ Sử dụng OpenAI (chỉ có OpenAI key)")
    else:
        provider = "custom"
        print("→ Sử dụng Custom mode (không có LLM keys)")
    
    # Create .env content
    env_content = f"""# API Keys for LLM Models
GOOGLE_API_KEY={google_key}
OPENAI_API_KEY={openai_key}

# Model Configuration
LLM_PROVIDER={provider}
GEMINI_MODEL=gemini-2.0-flash-exp

# App Configuration
DEBUG=True
LOG_LEVEL=INFO
"""
    
    # Write .env file
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n✅ Đã tạo file .env với provider: {provider}")
    
    # Show status
    print("\n📊 TRẠNG THÁI:")
    print(f"   🔑 Google API: {'✅' if google_key else '❌'}")
    print(f"   🔑 OpenAI API: {'✅' if openai_key else '❌'}")
    print(f"   🤖 Provider: {provider}")
    
    if provider == "gemini" and google_key:
        print(f"   🔥 Model: gemini-2.0-flash-exp")
    elif provider == "openai" and openai_key:
        print(f"   🧠 Model: gpt-3.5-turbo")
    
    print(f"\n🚀 Chạy: python main.py")
    print(f"🧪 Test: python test_langchain.py")

if __name__ == "__main__":
    setup_environment()