import base64
import json
import logging
import time
from typing import Dict, Any, Optional
import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.auth.schemas import JWTClaims
from app.auth.utils import extract_provider_from_claims

logger = logging.getLogger(__name__)

_jwks_clients: Dict[str, jwt.PyJWKClient] = {}
_token_cache: Dict[str, JWTClaims] = {}


def clear_jwt_cache() -> None:
    """Clears the in-memory JWT token cache."""
    _token_cache.clear()


def is_jwt_debug_enabled() -> bool:
    """Returns True if verbose JWT audit logging is enabled via config settings or logger level."""
    if getattr(settings, "JWT_DEBUG_LOGGING", False):
        return True
    if getattr(settings, "LOG_LEVEL", "INFO").upper() == "DEBUG":
        return True
    return logger.isEnabledFor(logging.DEBUG)


def log_jwt_debug(message: str, *args) -> None:
    """Logs detailed JWT audit information when debug logging is enabled."""
    if is_jwt_debug_enabled():
        logger.debug(message, *args)


def log_jwt_success(user_id: str, method: Optional[str] = None, path: Optional[str] = None) -> None:
    """Logs a single concise authentication log message on success."""
    if is_jwt_debug_enabled():
        logger.debug("[JWT AUDIT] JWT verification successful for user subject: %s", user_id)
    else:
        if method and path:
            logger.info("Authenticated request | method=%s | path=%s | user=%s", method, path, user_id)
        else:
            logger.info("Authenticated request | user=%s", user_id)


def _get_jwks_client(jwks_url: str) -> jwt.PyJWKClient:
    """Returns cached PyJWKClient instance to prevent redundant HTTP requests to JWKS endpoint."""
    if jwks_url not in _jwks_clients:
        _jwks_clients[jwks_url] = jwt.PyJWKClient(jwks_url, cache_keys=True)
    return _jwks_clients[jwks_url]


def _validate_jwt_claims(claims_dict: Dict[str, Any]) -> JWTClaims:
    """Validates decoded claim properties (expiration, sub, aud) and constructs JWTClaims."""
    exp = claims_dict.get("exp")
    if exp and time.time() > exp:
        logger.warning("JWT verification failed: token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = claims_dict.get("sub")
    if not sub:
        logger.warning("JWT verification failed: missing 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing subject identifier.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    aud = claims_dict.get("aud")
    if aud and aud not in ("authenticated", "anon", "authenticated,anon"):
        logger.warning("JWT verification failed: audience mismatch")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: audience mismatch.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    provider = extract_provider_from_claims(claims_dict)

    return JWTClaims(
        sub=str(sub),
        email=claims_dict.get("email"),
        provider=provider,
        iss=claims_dict.get("iss"),
        aud=str(aud) if aud else None,
        exp=exp,
        role=claims_dict.get("role"),
        user_metadata=claims_dict.get("user_metadata", {}),
        app_metadata=claims_dict.get("app_metadata", {}),
    )


def inspect_jwt_debug(token: str) -> Dict[str, Any]:
    """Helper to safely decode and log JWT header and payload for debugging."""
    try:
        parts = token.split(".")
        header_bytes = base64.urlsafe_b64decode(parts[0] + "=" * (-len(parts[0]) % 4))
        payload_bytes = base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4))
        header = json.loads(header_bytes)
        payload = json.loads(payload_bytes)

        header_summary = {
            "alg": header.get("alg"),
            "kid": header.get("kid"),
            "typ": header.get("typ"),
        }
        payload_summary = {
            "iss": payload.get("iss"),
            "aud": payload.get("aud"),
            "sub": payload.get("sub"),
            "role": payload.get("role"),
            "exp": payload.get("exp"),
        }
        log_jwt_debug("[JWT AUDIT] Header: %s", json.dumps(header_summary))
        log_jwt_debug("[JWT AUDIT] Payload: %s", json.dumps(payload_summary))
        return {"header": header, "payload": payload}
    except Exception as err:
        logger.warning("[JWT AUDIT] Could not parse token for audit: %s", err)
        return {}


def _verify_asymmetric_token(token: str, alg: str, key: str) -> Dict[str, Any]:
    """Handles RS256/ES256/PS256 signature verification via Supabase JWKS or PEM public key."""
    if settings.SUPABASE_URL:
        try:
            jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
            jwks_client = _get_jwks_client(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            decoded = jwt.decode(
                token,
                signing_key.key,
                algorithms=[alg],
                options={"verify_aud": False, "verify_exp": False},
            )
            log_jwt_debug("[JWT AUDIT] Verified %s via JWKS endpoint", alg)
            return decoded
        except Exception as jwks_err:
            logger.warning("[JWT AUDIT] JWKS verification failed (%s), attempting key fallback...", jwks_err)
            if key and key.startswith("-----BEGIN"):
                return jwt.decode(
                    token,
                    key,
                    algorithms=[alg],
                    options={"verify_aud": False, "verify_exp": False},
                )
            raise jwks_err
    elif key and key.startswith("-----BEGIN"):
        return jwt.decode(
            token,
            key,
            algorithms=[alg],
            options={"verify_aud": False, "verify_exp": False},
        )
    raise jwt.PyJWTError("Missing public key / JWKS for asymmetric token")


def _decode_and_verify_token(token: str, alg: str, key: str) -> Dict[str, Any]:
    """Routes token verification based on algorithm strategy."""
    if alg.startswith(("RS", "ES", "PS")):
        return _verify_asymmetric_token(token, alg, key)
    return jwt.decode(
        token,
        key,
        algorithms=["HS256", "HS384", "HS512"],
        options={"verify_aud": False, "verify_exp": False},
    )


def _check_cached_token(
    token: str,
    secret_key: Optional[str],
    method: Optional[str] = None,
    path: Optional[str] = None
) -> Optional[JWTClaims]:
    """Returns cached JWTClaims if valid and unexpired, otherwise removes stale cache entry."""
    if secret_key or token not in _token_cache:
        return None
    cached_claims = _token_cache[token]
    if cached_claims.exp and time.time() < (cached_claims.exp - 5):
        log_jwt_success(cached_claims.sub, method=method, path=path)
        return cached_claims
    _token_cache.pop(token, None)
    return None


def _cache_validated_token(token: str, claims: JWTClaims, secret_key: Optional[str]) -> None:
    """Caches validated claims and prunes expired tokens if capacity exceeds limit."""
    if secret_key:
        return
    _token_cache[token] = claims
    if len(_token_cache) > 500:
        now = time.time()
        expired_keys = [k for k, v in _token_cache.items() if v.exp and now >= v.exp]
        for k in expired_keys:
            _token_cache.pop(k, None)


def verify_jwt(
    token: str,
    secret_key: Optional[str] = None,
    method: Optional[str] = None,
    path: Optional[str] = None
) -> JWTClaims:
    """
    Verifies Supabase JWT token signature and claims structure.

    Raises HTTPException(401) on verification failure.
    Logs success/failure without exposing token or secrets.
    """
    if not token or not token.strip():
        logger.warning("JWT verification failed: empty token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing or empty.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fast path: Check in-memory cache for previously validated token
    cached_claims = _check_cached_token(token, secret_key, method=method, path=path)
    if cached_claims:
        return cached_claims

    # STEP 1 & 2: Diagnostic token inspection
    debug_info = inspect_jwt_debug(token)
    header = debug_info.get("header", {})
    alg = header.get("alg", "HS256")
    kid = header.get("kid")

    key = secret_key or getattr(settings, "SUPABASE_JWT_SECRET", None) or settings.SUPABASE_SERVICE_ROLE_KEY
    key_type = "PEM" if (key and key.startswith("-----BEGIN")) else "Symmetric/String Secret"
    log_jwt_debug("[JWT AUDIT] Selected Alg: %s | Key Type: %s | kid: %s", alg, key_type, kid)

    try:
        decoded_claims = _decode_and_verify_token(token, alg, key)
        validated_claims = _validate_jwt_claims(decoded_claims)
        log_jwt_success(validated_claims.sub, method=method, path=path)
        _cache_validated_token(token, validated_claims, secret_key)
        return validated_claims
    except (jwt.PyJWTError, ValueError) as exc:
        logger.warning("JWT verification failed due to decode/format error (%s): %s", type(exc).__name__, exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or corrupted authentication token signature.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during JWT verification: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

