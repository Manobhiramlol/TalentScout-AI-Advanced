"""
Components package for TalentScout AI
"""

# Import only the functions that actually exist
from .sidebar import render_sidebar
from .advanced_chat import render_chat_interface

# Make functions available at package level
__all__ = [
    'render_sidebar',
    'render_chat_interface'
]
