import streamlit as st
import asyncio
import json
from datetime import datetime
from smart_orchestrator import SmartOrchestrator

# Page config
st.set_page_config(
    page_title="🛫 Smart Booking Agent",
    page_icon="✈️",
    layout="wide"
)

# Initialize orchestrator
@st.cache_resource
def get_orchestrator():
    return SmartOrchestrator()

orchestrator = get_orchestrator()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Main UI
st.title("🛫 Smart Booking Agent")
st.markdown("*AI-powered flight booking assistant with context awareness*")

# Sidebar - Context Info
with st.sidebar:
    st.header("📊 Session Info")
    
    # User ID
    st.text(f"User ID: {st.session_state.user_id}")
    
    # Context display
    if hasattr(orchestrator, 'user_contexts') and st.session_state.user_id in orchestrator.user_contexts:
        context = orchestrator.user_contexts[st.session_state.user_id]
        
        st.subheader("🧠 Current Context")
        
        # Slots info
        if hasattr(context, 'slots') and context.slots:
            st.write("**Active Slots:**")
            for key, value in context.slots.items():
                if key not in ['last_search_results', 'original_message']:
                    st.text(f"• {key}: {value}")
        
        # Query history
        if hasattr(context, 'query_history') and context.query_history:
            st.write("**Query History:**")
            for i, query in enumerate(context.query_history[-5:], 1):
                st.text(f"{i}. {query}")
        
        # Search results
        if hasattr(context, 'slots') and context.slots.get('last_search_results'):
            flights = context.slots['last_search_results']
            st.write(f"**Search Results:** {len(flights)} flights")
    
    # Clear context button
    if st.button("🔄 Clear Context"):
        if st.session_state.user_id in orchestrator.user_contexts:
            del orchestrator.user_contexts[st.session_state.user_id]
        st.session_state.messages = []
        st.rerun()

# Main chat area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat")
    
    # Display messages
    for msg_idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display suggestions if available
            if message["role"] == "assistant" and "suggestions" in message:
                st.write("**Quick Actions:**")
                cols = st.columns(len(message["suggestions"]))
                for i, suggestion in enumerate(message["suggestions"]):
                    with cols[i]:
                        if st.button(suggestion, key=f"sug_{msg_idx}_{i}"):
                            # Add suggestion as user message
                            st.session_state.messages.append({
                                "role": "user", 
                                "content": suggestion
                            })
                            st.rerun()

    # Chat input
    if prompt := st.chat_input("Nhập tin nhắn của bạn..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Đang xử lý..."):
                try:
                    response = asyncio.run(
                        orchestrator.process_message(st.session_state.user_id, prompt)
                    )
                    
                    st.markdown(response["response"])
                    
                    # Add assistant message with suggestions
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["response"],
                        "suggestions": response.get("suggestions", [])
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Lỗi: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

with col2:
    st.header("📋 Details")
    
    # Flight results display
    if (hasattr(orchestrator, 'user_contexts') and 
        st.session_state.user_id in orchestrator.user_contexts):
        
        context = orchestrator.user_contexts[st.session_state.user_id]
        
        if (hasattr(context, 'slots') and 
            context.slots.get('last_search_results')):
            
            flights = context.slots['last_search_results']
            
            st.subheader("✈️ Available Flights")
            
            for i, flight in enumerate(flights, 1):
                with st.expander(f"Flight {i}: {flight['airline']} {flight['flight_id']}"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write(f"**Route:** {flight['from_city']} → {flight['to_city']}")
                        st.write(f"**Time:** {flight['time']}")
                        st.write(f"**Date:** {flight['date']}")
                    
                    with col_b:
                        st.write(f"**Price:** {flight['price']:,} VNĐ")
                        st.write(f"**Seats:** {flight['seats_left']} left")
                        st.write(f"**Class:** {flight['class_type']}")
                    
                    # Book button
                    if st.button(f"📝 Book Flight {i}", key=f"book_{flight['service_id']}_{i}"):
                        book_msg = f"Đặt vé {flight['airline']} {flight['flight_id']}"
                        st.session_state.messages.append({
                            "role": "user", 
                            "content": book_msg
                        })
                        st.rerun()
    
    # Debug info (collapsible)
    with st.expander("🔧 Debug Info"):
        if (hasattr(orchestrator, 'user_contexts') and 
            st.session_state.user_id in orchestrator.user_contexts):
            
            context = orchestrator.user_contexts[st.session_state.user_id]
            
            st.write("**Full Context:**")
            st.json({
                "user_id": context.user_id,
                "intent": getattr(context, 'intent', None),
                "previous_intent": getattr(context, 'previous_intent', None),
                "slots_count": len(getattr(context, 'slots', {})),
                "query_history_count": len(getattr(context, 'query_history', [])),
                "last_updated": str(getattr(context, 'last_updated', None))
            })

# Footer
st.markdown("---")
st.markdown("*Powered by Smart Orchestrator with Context Awareness*")