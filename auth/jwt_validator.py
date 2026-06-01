import os
from functools import wraps

import httpx
from flask import jsonify, request
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

AUTHACTION_DOMAIN = os.getenv("AUTHACTION_DOMAIN")
AUTHACTION_AUDIENCE = os.getenv("AUTHACTION_AUDIENCE")

_jwks_cache: dict | None = None


def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        jwks_uri = f"https://{AUTHACTION_DOMAIN}/.well-known/jwks.json"
        response = httpx.get(jwks_uri)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache


def _find_rsa_key(token: str) -> dict:
    jwks = _get_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    # Key not found — could be a rotation; bust cache and retry once
    global _jwks_cache
    _jwks_cache = None
    jwks = _get_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    raise ValueError("Unable to find matching public key")


def verify_token(token: str) -> dict:
    rsa_key = _find_rsa_key(token)
    return jwt.decode(
        token,
        rsa_key,
        algorithms=["RS256"],
        audience=AUTHACTION_AUDIENCE,
        issuer=f"https://{AUTHACTION_DOMAIN}",
    )


def require_auth(f):
    """Decorator that validates the Bearer JWT before calling the route handler."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = verify_token(token)
        except ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except (JWTError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 401

        request.current_payload = payload
        return f(*args, **kwargs)

    return decorated
