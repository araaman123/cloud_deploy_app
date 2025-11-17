"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles."""
    ADMIN = "admin"
    USER = "user"
    DEVELOPER = "developer"


class AppType(str, Enum):
    """Application types."""
    PYTHON = "python"
    NODE = "node"
    STATIC = "static"


class DeploymentStatus(str, Enum):
    """Deployment statuses."""
    PENDING = "pending"
    BUILDING = "building"
    BUILT = "built"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""
    github_id: int


class UserResponse(UserBase):
    """User response schema."""
    id: str
    github_id: int
    avatar_url: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Application Schemas
class AppBase(BaseModel):
    """Base application schema."""
    name: str
    description: Optional[str] = None
    github_repo_url: str
    github_branch: str = "main"
    app_type: AppType
    port: int = 8000
    cpu_limit: str = "1000m"
    memory_limit: str = "512Mi"
    replicas: int = 1


class AppCreate(AppBase):
    """Application creation schema."""
    environment_variables: Optional[dict] = None


class AppUpdate(BaseModel):
    """Application update schema."""
    description: Optional[str] = None
    cpu_limit: Optional[str] = None
    memory_limit: Optional[str] = None
    replicas: Optional[int] = None
    environment_variables: Optional[dict] = None


class AppResponse(AppBase):
    """Application response schema."""
    id: str
    status: DeploymentStatus
    namespace: str
    domain: Optional[str]
    tls_enabled: bool
    image_uri: Optional[str]
    image_tag: Optional[str]
    created_at: datetime
    updated_at: datetime
    deployed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Deployment Schemas
class DeploymentBase(BaseModel):
    """Base deployment schema."""
    pass


class DeploymentResponse(DeploymentBase):
    """Deployment response schema."""
    id: str
    app_id: str
    status: DeploymentStatus
    commit_hash: str
    commit_message: Optional[str]
    image_uri: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


# Log Schemas
class LogResponse(BaseModel):
    """Log response schema."""
    id: str
    app_id: str
    level: str
    message: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Metric Schemas
class MetricResponse(BaseModel):
    """Metric response schema."""
    id: str
    app_id: str
    metric_name: str
    metric_value: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


# GitHub OAuth
class GitHubUser(BaseModel):
    """GitHub user data from OAuth."""
    id: int
    login: str
    email: str
    avatar_url: str
    name: str


class AuthToken(BaseModel):
    """Authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# Webhook Schemas
class GitHubPushEvent(BaseModel):
    """GitHub push event webhook."""
    ref: str
    before: str
    after: str
    repository: dict
    pusher: dict
    commits: list
    head_commit: dict
