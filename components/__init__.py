"""
TalentScout AI Components Package
Streamlit UI components for advanced interview system
"""

__version__ = "2.0.0"
__author__ = "TalentScout AI Team"

from .sidebar import render_sidebar, sidebar_renderer
from .advanced_chat import render_chat_interface  # ← Use actual function name
from .dashboard import render_dashboard
from .analytics import render_analytics

__all__ = [
    # Sidebar
    'render_sidebar',
    'sidebar_renderer',
    
    # Chat Interface  
    'render_chat_interface',  # ← Update this
    
    # Dashboard
    'render_dashboard',
    
    # Analytics
    'render_analytics'
]
