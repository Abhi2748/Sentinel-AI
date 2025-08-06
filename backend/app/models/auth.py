"""
Authentication and authorization models.
"""

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class AuthLevel(Enum):
    USER = "user"
    TEAM_ADMIN = "team_admin"
    COMPANY_ADMIN = "company_admin"
    SYSTEM_ADMIN = "system_admin"


class AuthContext(BaseModel):
    """Authentication context for requests."""
    
    user_id: str
    team_id: Optional[str] = None
    company_id: Optional[str] = None
    auth_level: AuthLevel = AuthLevel.USER
    permissions: list[str] = []
    
    class Config:
        use_enum_values = True


class AuthRequest(BaseModel):
    """Authentication request model."""
    
    username: str
    password: str


class AuthResponse(BaseModel):
    """Authentication response model."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    team_id: Optional[str] = None
    company_id: Optional[str] = None
    auth_level: AuthLevel
    permissions: list[str] = []


class TokenData(BaseModel):
    """Token data for JWT."""
    
    user_id: str
    team_id: Optional[str] = None
    company_id: Optional[str] = None
    auth_level: AuthLevel
    permissions: list[str] = []