"""
Zynx AGI Core Foundation - Main FastAPI Application

Provides the main FastAPI application with all routers, middleware,
and startup/shutdown events for the Zynx AGI Core Foundation.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.core.zpdl import generate_zpdl_metadata, get_bangkok_timestamp
from app.api.v1.llm import router as llm_router
from app.api.v1.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    try:
        # Create database tables (fallback if migrations haven't been run)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"⚠️  Database setup warning: {e}")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down Zynx AGI Core Foundation")


# Create FastAPI application
app = FastAPI(
    title="Zynx AGI Core Foundation",
    description="Empathy-first AI platform with IP provenance tracking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(llm_router)
app.include_router(users_router)


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Zynx AGI Core Foundation",
        "version": "1.0.0",
        "description": "Empathy-first AI platform with IP provenance tracking",
        "author": "Chanont Wankaew",
        "timestamp": get_bangkok_timestamp()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "zynx-agi-core",
        "timestamp": get_bangkok_timestamp(),
        "components": {
            "database": "operational",
            "llm_proxy": "operational",
            "api": "operational"
        }
    }


@app.get("/metadata/template")
async def get_metadata_template():
    """
    Get ZPDL metadata template.
    
    Returns a template showing the structure of ZPDL metadata
    used for IP provenance tracking.
    """
    sample_content = "This is sample content for metadata generation"
    
    template = generate_zpdl_metadata(
        content=sample_content,
        artifact_type="template",
        additional_metadata={
            "description": "Sample ZPDL metadata template",
            "usage": "Use this structure for tracking IP provenance"
        }
    )
    
    return {
        "template": template,
        "description": "ZPDL (Zynx Provenance Data Language) metadata template",
        "fields": {
            "zpdl_version": "Version of ZPDL specification",
            "timestamp": "Asia/Bangkok timezone timestamp",
            "sha256": "SHA256 hash of artifact content",
            "artifact_type": "Type classification of the artifact",
            "author": "Author of the artifact",
            "provenance": "Source and repository information"
        }
    }


@app.post("/artifact/hash")
async def hash_artifact(artifact: dict):
    """
    Generate SHA256 hash and ZPDL metadata for an artifact.
    
    Accepts artifact data and returns hash and full ZPDL metadata.
    """
    try:
        # Convert artifact to string for hashing
        if isinstance(artifact, dict):
            content = str(artifact.get("content", ""))
            artifact_type = artifact.get("type", "unknown")
        else:
            content = str(artifact)
            artifact_type = "unknown"
        
        metadata = generate_zpdl_metadata(
            content=content,
            artifact_type=artifact_type,
            additional_metadata=artifact.get("metadata", {})
        )
        
        return {
            "success": True,
            "zpdl_metadata": metadata,
            "hash": metadata["sha256"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process artifact: {str(e)}")


@app.get("/info")
async def get_info():
    """Application information and configuration."""
    return {
        "app": {
            "name": "Zynx AGI Core Foundation",
            "version": "1.0.0",
            "author": "Chanont Wankaew",
            "description": "Empathy-first AI platform with IP provenance tracking"
        },
        "features": [
            "FastAPI Application with async support",
            "PostgreSQL database with Alembic migrations",
            "MinIO S3-compatible object storage",
            "Redis caching and session management", 
            "LLM Proxy for OpenAI, Claude, Ollama",
            "IP Provenance with ZPDL metadata tracking",
            "Agent manifest management",
            "User authentication system"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "llm": "/api/v1/llm",
            "users": "/api/v1/users",
            "metadata": "/metadata/template",
            "hash": "/artifact/hash"
        },
        "timestamp": get_bangkok_timestamp()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )