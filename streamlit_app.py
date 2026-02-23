"""
Streamlit UI for Bangladesh Knowledge Agent
ChatGPT-style interface for interacting with the AI agent
"""

import streamlit as st
import sys
import os
from datetime import datetime
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.main_agent import BangladeshKnowledgeAgent
from utils.cache_manager import CacheManager
from utils.query_logger import QueryLogger

# Page configuration
st.set_page_config(
    page_title="Bangladesh Knowledge Agent",
    page_icon="🇧🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-style interface
def load_css():
    st.markdown("""
    <style>
    /* Hide ALL Streamlit default elements */
.stApp header {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

.stApp > div {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
    margin-top: 0 !important;
}

.main .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}

/* Remove all default margins and padding */
.stApp > div > div > div > div {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

.main {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 1200px;
}
    
    .chat-container {
        border: 1px solid #e1e5e9;
        border-radius: 12px;
        overflow: hidden;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem;
        text-align: center;
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    .chat-messages {
        padding: 0.75rem;
        height: 500px;
        overflow-y: auto;
        background: #f8f9fa;
    }
    
    .message {
        margin-bottom: 1.5rem;
        display: flex;
        align-items: flex-start;
    }
    
    .user-message {
        justify-content: flex-end;
    }
    
    .message-content {
        max-width: 70%;
        padding: 1rem;
        border-radius: 18px;
        word-wrap: break-word;
    }
    
    .user-message .message-content {
        background: #007bff;
        color: white;
        border-bottom-right-radius: 4px;
    }
    
    .assistant-message .message-content {
        background: white;
        border: 1px solid #e1e5e9;
        border-bottom-left-radius: 4px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        color: #212529;
        line-height: 1.5;
    }
    
    .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        margin: 0 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 0.9rem;
    }
    
    .user-avatar {
        background: #007bff;
    }
    
    .assistant-avatar {
        background: #28a745;
    }
    
    .chat-input {
        padding: 1.5rem;
        background: white;
        border-top: 1px solid #e1e5e9;
    }
    
    .input-container {
        display: flex;
        gap: 0.5rem;
        align-items: flex-end;
    }
    
    .input-text {
        flex: 1;
    }
    
    .send-button {
        background: #007bff;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
        transition: background 0.2s;
    }
    
    .send-button:hover {
        background: #0056b3;
    }
    
    .metadata {
        font-size: 0.8rem;
        color: #6c757d;
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 3px solid #007bff;
        color: #495057;
    }
    
    .sidebar-section {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #e1e5e9;
    }
    
    .sidebar-title {
        font-weight: bold;
        color: #495057;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .stat-label {
        font-size: 0.8rem;
        opacity: 0.9;
    }
    
    .example-query {
        background: #f8f9fa;
        padding: 0.5rem;
        border-radius: 6px;
        margin-bottom: 0.25rem;
        cursor: pointer;
        transition: background 0.2s;
        font-size: 0.85rem;
    }
    
    .example-query:hover {
        background: #e9ecef;
    }
    
    .confidence-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    
    .confidence-high {
        background: #d4edda;
        color: #155724;
    }
    
    .confidence-medium {
        background: #fff3cd;
        color: #856404;
    }
    
    .confidence-low {
        background: #f8d7da;
        color: #721c24;
    }
    
    .tool-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        background: #e9ecef;
        color: #495057;
        margin-right: 0.5rem;
    }
    
    .cached-indicator {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        background: #d1ecf1;
        color: #0c5460;
    }
    
    .clear-button {
        background: #dc3545;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    .clear-button:hover {
        background: #c82333;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        st.session_state.agent = BangladeshKnowledgeAgent()
    if 'session_id' not in st.session_state:
        st.session_state.session_id = st.session_state.agent.session_id

def get_confidence_class(confidence):
    """Get CSS class for confidence score"""
    if confidence >= 0.8:
        return "confidence-high"
    elif confidence >= 0.6:
        return "confidence-medium"
    else:
        return "confidence-low"

def format_confidence(confidence):
    """Format confidence score with emoji"""
    if confidence >= 0.8:
        return f"🟢 {confidence:.2f}"
    elif confidence >= 0.6:
        return f"🟡 {confidence:.2f}"
    else:
        return f"🔴 {confidence:.2f}"

def render_message(message, index):
    """Render a single message"""
    if message['role'] == 'user':
        st.markdown(f"""
        <div class="message user-message">
            <div class="message-content">
                {message['content']}
            </div>
            <div class="message-avatar user-avatar">U</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Assistant message
        metadata = message.get('metadata', {})
        confidence = metadata.get('result_confidence', 0)
        tool_used = metadata.get('tool_used', 'unknown')
        cached = metadata.get('cached', False)
        execution_time = metadata.get('execution_time', 0)
        
        confidence_class = get_confidence_class(confidence)
        confidence_formatted = format_confidence(confidence)
        
        # Use the clean response directly
        content = message['content']
        
        # Display content
        st.markdown(f"""
        <div class="message assistant-message">
            <div class="message-avatar assistant-avatar">🇧🇩</div>
            <div class="message-content">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display metadata using Streamlit components
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.markdown(f'<span class="confidence-badge {confidence_class}">Confidence: {confidence_formatted}</span>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span class="tool-badge">Tool: {tool_used}</span>', unsafe_allow_html=True)
        with col3:
            if cached:
                st.markdown('<span class="cached-indicator">⚡ Cached</span>', unsafe_allow_html=True)
        
        # Time display
        st.markdown(f'<div style="font-size: 0.8rem; color: #6c757d; margin-top: 0.5rem;">⏱️ Time: {execution_time:.3f}s</div>', unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with statistics and examples"""
    st.sidebar.markdown("## 📊 Session Statistics")
    
    # Get session stats
    try:
        session_summary = st.session_state.agent.query_logger.get_session_summary(st.session_state.session_id)
        
        st.sidebar.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{session_summary.get('total_queries', 0)}</div>
            <div class="stat-label">Total Queries</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{session_summary.get('avg_confidence', 0):.2f}</div>
            <div class="stat-label">Avg Confidence</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{session_summary.get('cache_hit_rate', 0):.1f}%</div>
            <div class="stat-label">Cache Hit Rate</div>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.sidebar.error(f"Error loading stats: {e}")
    
    # Example queries
    st.sidebar.markdown("## 💡 Example Queries")
    
    examples = [
        ("🏛️ Institutions", [
            "How many universities are in Dhaka?",
            "List all universities in Bangladesh",
            "Find colleges established after 1950",
            "What engineering universities are available?"
        ]),
        ("🏥 Hospitals", [
            "List hospitals with emergency services",
            "Hospitals with more than 1000 beds",
            "Medical colleges in Dhaka",
            "What private hospitals are available?"
        ]),
        ("🍽️ Restaurants", [
            "What restaurants serve Italian food?",
            "Bangladeshi restaurants with high ratings",
            "Restaurants in Chattogram serving Italian food",
            "Find restaurants with medium price range"
        ]),
        ("🌐 Web Search", [
            "What is healthcare policy of Bangladesh?",
            "Cultural festivals in Bangladesh",
            "Economic policies of Bangladesh"
        ])
    ]
    
    # Generate unique keys for example buttons
    example_counter = 0
    
    for category, queries in examples:
        with st.sidebar.expander(category):
            for query in queries:
                if st.button(query, key=f"example_{example_counter}"):
                    st.session_state.example_query = query
                example_counter += 1
    
    # Clear chat button
    st.sidebar.markdown("## 🗑️ Chat Management")
    if st.sidebar.button("Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

def render_chat_interface():
    """Render main chat interface"""
    # Chat container
    st.markdown("""
    <div class="chat-container">
        <div class="chat-header">
            🇧🇩 Bangladesh Knowledge Agent
        </div>
        <div class="chat-messages">
    """, unsafe_allow_html=True)
    
    # Render messages
    for i, message in enumerate(st.session_state.messages):
        render_message(message, i)
    
    # Auto-scroll to bottom
    if st.session_state.messages:
        st.markdown("""
        <script>
            var chatMessages = document.querySelector('.chat-messages');
            chatMessages.scrollTop = chatMessages.scrollHeight;
        </script>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown('<div class="chat-input">', unsafe_allow_html=True)
    
    # Input container
    col1, col2 = st.columns([4, 1])
    
    # Get current input value from session state or use default
    current_input = st.session_state.get('current_input', '')
    
    with col1:
        user_input = st.text_area(
            "Type your message here...",
            value=current_input,
            key="user_input",
            height=100,
            placeholder="Ask about Bangladesh institutions, hospitals, restaurants, or general knowledge...",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button(
            "📤 Send",
            type="primary",
            use_container_width=True,
            disabled=not user_input.strip()
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Update current input in session state for next render
    st.session_state.current_input = user_input
    
    return user_input, send_button

def main():
    """Main application"""
    # Load custom CSS
    load_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Page title - absolutely minimal
    st.markdown('<h1 style="margin: 0; padding: 0; font-size: 1.3rem;">🇧🇩 Bangladesh Knowledge Agent</h1>', unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Handle example query from sidebar
    if 'example_query' in st.session_state:
        st.session_state.current_input = st.session_state.example_query
        del st.session_state.example_query
    
    # Render chat interface
    user_input, send_button = render_chat_interface()
    
    # Handle message submission
    if (send_button or st.session_state.get('submit_on_enter', False)) and user_input.strip():
        # Add user message
        user_message = {
            'role': 'user',
            'content': user_input.strip(),
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.messages.append(user_message)
        
        # Get AI response - use include_metadata=False to get clean response
        with st.spinner("🤔 Thinking..."):
            try:
                response = st.session_state.agent.query(user_input.strip(), include_metadata=False)
                
                if response['success']:
                    assistant_message = {
                        'role': 'assistant',
                        'content': response['response'],
                        'metadata': response.get('metadata', {}),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    assistant_message = {
                        'role': 'assistant',
                        'content': f"❌ Error: {response['response']}",
                        'metadata': {'error': True},
                        'timestamp': datetime.now().isoformat()
                    }
                
                st.session_state.messages.append(assistant_message)
                
            except Exception as e:
                error_message = {
                    'role': 'assistant',
                    'content': f"❌ An error occurred: {str(e)}",
                    'metadata': {'error': True},
                    'timestamp': datetime.now().isoformat()
                }
                st.session_state.messages.append(error_message)
        
        # Clear input and rerun
        st.session_state.submit_on_enter = False
        st.rerun()
    
    # Handle Enter key submission
    if user_input and st.session_state.get('user_input_changed', False):
        st.session_state.submit_on_enter = True
        st.session_state.user_input_changed = False

if __name__ == "__main__":
    main()
