"""
FastAPI application for TalentScout AI
Main ASGI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

# Create FastAPI app
app = FastAPI(
    title="TalentScout AI API",
    description="Advanced AI-powered interview system",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api/v1")

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "TalentScout AI API is running", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TalentScout AI API"}
