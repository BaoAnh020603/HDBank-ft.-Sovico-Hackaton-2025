import streamlit as st
import requests
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="🛫 Booking Agent",
    page_icon="✈️",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000/chat"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Header
st.title("🛫 AI Booking Agent")
st.caption("Trợ lý đặt vé máy bay thông minh")

# Chat interface
chat_container = st.container()

# Display chat messages
with chat_container:
    for msg_idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show suggestions if available
            if message["role"] == "assistant" and "suggestions" in message:
                cols = st.columns(len(message["suggestions"]))
                for i, suggestion in enumerate(message["suggestions"]):
                    if cols[i].button(suggestion, key=f"sug_{msg_idx}_{i}"):
                        # Add suggestion as user message
                        st.session_state.messages.append({
                            "role": "user", 
                            "content": suggestion
                        })
                        st.rerun()

# Chat input
if prompt := st.chat_input("Nhập tin nhắn..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý..."):
            try:
                response = requests.post(API_URL, json={
                    "user_id": st.session_state.user_id,
                    "message": prompt
                })
                
                if response.status_code == 200:
                    data = response.json()
                    assistant_message = data["response"]
                    suggestions = data.get("suggestions", [])
                    
                    # Display response
                    st.write(assistant_message)
                    
                    # Add to session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_message,
                        "suggestions": suggestions
                    })
                    
                    # Show context info in sidebar
                    if "context" in data and "session_context" in data["context"]:
                        with st.sidebar:
                            st.divider()
                            st.subheader("🔍 Session Context")
                            st.json(data["context"]["session_context"])
                    
                else:
                    st.error(f"API Error: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")
                print(f"DEBUG: Full error: {e}")
                if response:
                    print(f"DEBUG: Response content: {response.text}")

# Sidebar
with st.sidebar:
    st.subheader("⚙️ Settings")
    
    # API Configuration
    st.subheader("🔑 API Configuration")
    
    # Google API Key input
    api_key = st.text_input(
        "Google API Key", 
        type="password",
        help="Nhập GOOGLE_API_KEY của bạn"
    )
    
    # Gemini model selection
    model_options = [
        "gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-pro"
    ]
    selected_model = st.selectbox(
        "Gemini Model",
        options=model_options,
        index=0
    )
    
    # Update environment variables
    if api_key:
        import os
        os.environ["GOOGLE_API_KEY"] = api_key
        os.environ["GEMINI_MODEL"] = selected_model
        os.environ["LLM_PROVIDER"] = "gemini"
        st.success("✅ Gemini API Key updated")
    else:
        st.warning("⚠️ Cần nhập Google API Key")
    
    st.divider()
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.write(f"**User ID:** `{st.session_state.user_id}`")
    st.write(f"**Model:** `{selected_model}`")
    st.write(f"**Provider:** `Gemini`")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    quick_actions = [
        "Tìm vé HN → SGN ngày mai",
        "Vé rẻ nhất cuối tuần",
        "Kiểm tra giá vé",
        "Đặt vé ngay"
    ]
    
    for action in quick_actions:
        if st.button(action, key=f"quick_{action}"):
            st.session_state.messages.append({"role": "user", "content": action})
            st.rerun()