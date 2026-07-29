from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class JWTClaims(BaseModel):
    """
    Decoded claims extracted from a verified Supabase JWT.
    """
    sub: str = Field(..., description="User UUID string")
    email: Optional[str] = Field(None, description="User email address")
    provider: Optional[str] = Field("email", description="Authentication provider")
    iss: Optional[str] = Field(None, description="JWT Issuer")
    aud: Optional[str] = Field(None, description="JWT Audience")
    exp: Optional[int] = Field(None, description="Expiration timestamp")
    role: Optional[str] = Field(None, description="Supabase user role")
    user_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    app_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AuthenticatedUser(BaseModel):
    """
    Schema representing an authenticated user instance across the system.
    """
    id: str = Field(..., description="User UUID string")
    email: Optional[str] = Field(None, description="User email address")
    provider: str = Field("email", description="Auth provider (e.g. email, google)")


class ProfileResponse(BaseModel):
    """
    Schema for profile responses returned by /me and /auth/sync-profile.
    """
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str = "email"

    model_config = ConfigDict(from_attributes=True)
