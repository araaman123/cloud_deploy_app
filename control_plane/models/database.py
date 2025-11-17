"""Database models for the control plane."""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from database.init import Base
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    DEVELOPER = "developer"


class User(Base):
    """User model for storing user information."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    avatar_url = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    apps = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"


class APIKey(Base):
    """API Key model for authentication."""
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    key_hash = Column(String, unique=True, index=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<APIKey {self.name}>"


class AppType(str, enum.Enum):
    """Application type enumeration."""
    PYTHON = "python"
    NODE = "node"
    STATIC = "static"


class DeploymentStatus(str, enum.Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    BUILDING = "building"
    BUILT = "built"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"


class Application(Base):
    """Application model for storing deployed applications."""
    __tablename__ = "applications"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    name = Column(String, index=True)
    description = Column(Text)
    github_repo_url = Column(String)
    github_branch = Column(String, default="main")
    app_type = Column(Enum(AppType))
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING)
    
    # Configuration
    port = Column(Integer, default=8000)
    environment_variables = Column(Text)  # JSON string
    
    # Infrastructure
    namespace = Column(String, unique=True)
    domain = Column(String, unique=True)
    tls_enabled = Column(Boolean, default=True)
    
    # Resource allocation
    cpu_limit = Column(String, default="1000m")
    memory_limit = Column(String, default="512Mi")
    replicas = Column(Integer, default=1)
    
    # Docker image
    image_uri = Column(String)
    image_tag = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deployed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="apps")
    deployments = relationship("Deployment", back_populates="app", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Application {self.name}>"


class Deployment(Base):
    """Deployment model for tracking application deployments."""
    __tablename__ = "deployments"
    
    id = Column(String, primary_key=True, index=True)
    app_id = Column(String, ForeignKey("applications.id"), index=True)
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING)
    commit_hash = Column(String)
    commit_message = Column(Text)
    image_uri = Column(String)
    
    # Deployment info
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Relationships
    app = relationship("Application", back_populates="deployments")
    
    def __repr__(self):
        return f"<Deployment {self.id}>"


class Log(Base):
    """Application logs model."""
    __tablename__ = "logs"
    
    id = Column(String, primary_key=True, index=True)
    app_id = Column(String, ForeignKey("applications.id"), index=True)
    deployment_id = Column(String, ForeignKey("deployments.id"))
    level = Column(String, default="INFO")  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Log {self.level} {self.timestamp}>"


class Metric(Base):
    """Application metrics model."""
    __tablename__ = "metrics"
    
    id = Column(String, primary_key=True, index=True)
    app_id = Column(String, ForeignKey("applications.id"), index=True)
    metric_name = Column(String)  # cpu_usage, memory_usage, request_count, etc.
    metric_value = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Metric {self.metric_name}>"
