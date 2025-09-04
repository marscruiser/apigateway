import base64
import json
from functools import wraps
from typing import Callable, List
from apigateway.core.adapters.base_adapter import FrameworkAdapter
from apigateway.core.adapters.flask import FlaskAdapter

class AuthError(Exception):
    """Custom exception for authentication errors."""
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def simple_decode(token: str) -> dict:
    """Decodes the JWT payload without verifying the signature."""
    try:
        payload_b64 = token.split('.')[1]
        payload_b64 += '=' * (-len(payload_b64) % 4)
        decoded_payload = base64.urlsafe_b64decode(payload_b64)
        return json.loads(decoded_payload)
    except Exception:
        raise AuthError("Invalid token format", status_code=401)

# This decorator just checks if a user is logged in
def require_token(adapter: FrameworkAdapter):
    """Decorator that requires a token but does not check roles."""
    def decorator(func: Callable):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                auth_header = adapter.get_auth_header(*args, **kwargs)
                if not auth_header or not auth_header.startswith("Bearer "):
                    raise AuthError("Authorization header is missing or invalid")
                token = auth_header.split(" ")[1]
                payload = simple_decode(token)
                kwargs['user_payload'] = payload
                return func(*args, **kwargs)
            except AuthError as e:
                return adapter.handle_auth_error(e)
        return sync_wrapper
    return decorator

# --- NEW DECORATOR FOR ROLE-BASED ACCESS ---
def require_access(adapter: FrameworkAdapter, allowed_roles: List[str]):
    """
    Decorator that requires a token AND checks if the user's role
    is in the list of allowed roles.
    """
    def decorator(func: Callable):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                auth_header = adapter.get_auth_header(*args, **kwargs)
                if not auth_header or not auth_header.startswith("Bearer "):
                    raise AuthError("Authorization header is missing or invalid")
                
                token = auth_header.split(" ")[1]
                payload = simple_decode(token)
                
                # Role Check
                user_role = payload.get("role")
                if not user_role or user_role not in allowed_roles:
                    # Use 403 Forbidden for authorization errors
                    raise AuthError("You do not have permission to access this resource", status_code=403)
                
                kwargs['user_payload'] = payload
                return func(*args, **kwargs)
            except AuthError as e:
                return adapter.handle_auth_error(e)
        return sync_wrapper
    return decorator

def require_flask_token():
    """Convenience decorator for Flask (any role)."""
    return require_token(adapter=FlaskAdapter())

def require_flask_access(allowed_roles: List[str]):
    """Convenience decorator for Flask (specific roles)."""
    return require_access(adapter=FlaskAdapter(), allowed_roles=allowed_roles)