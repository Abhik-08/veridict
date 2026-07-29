from typing import Optional, Dict, Any


def extract_bearer_token(header_value: Optional[str]) -> Optional[str]:
    """
    Extracts raw JWT token from HTTP Authorization header.
    Format: 'Bearer <token>'
    """
    if not header_value:
        return None

    parts = header_value.strip().split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def extract_provider_from_claims(claims: Dict[str, Any]) -> str:
    """
    Extracts provider string from JWT claims (app_metadata or user_metadata).
    Defaults to 'email'.
    """
    app_meta = claims.get("app_metadata", {})
    if isinstance(app_meta, dict) and "provider" in app_meta:
        return str(app_meta["provider"])

    user_meta = claims.get("user_metadata", {})
    if isinstance(user_meta, dict) and "provider" in user_meta:
        return str(user_meta["provider"])

    return "email"
