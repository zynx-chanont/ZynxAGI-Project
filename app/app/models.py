from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """User model for authentication and user management."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship with sessions
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """Session model for user session management."""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship with user
    user = relationship("User", back_populates="sessions")


class AgentManifest(Base):
    """Agent manifest model for storing agent metadata and capabilities."""
    __tablename__ = "agent_manifests"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50), nullable=False)
    core_function = Column(Text)
    key_capabilities = Column(JSON)  # Array of capability strings
    mcp_command = Column(String(100))  # MCP slash command
    status = Column(String(50), index=True, nullable=False)  # Live, Planned, Deprecated
    metadata = Column(JSON)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())