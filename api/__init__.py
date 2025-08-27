"""
TalentScout AI API Package
API routes and handlers
"""

__version__ = "2.0.0"
__author__ = "TalentScout AI Team"

# Import API modules when they exist
try:
    from .routes import *
except ImportError:
    pass

__all__ = [
    'routes'
]
