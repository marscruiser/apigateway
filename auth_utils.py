import os
import json
import base64
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from jwcrypto import jwt, jwk
from jwcrypto.common import JWException

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-for-dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# --- Create a symmetric key object for jwcrypto ---
# 1. Convert the hex secret key from the .env file into raw bytes
raw_key = bytes.fromhex(SECRET_KEY)
# 2. Base64url-encode the raw bytes, as required by the library
encoded_key = base64.urlsafe_b64encode(raw_key).decode('ascii')
# 3. Create the JWK object from the correctly formatted base64url string
JWK_KEY = jwk.JWK(k=encoded_key, kty='oct')


class AuthError(Exception):
    """Custom exception for authentication errors."""
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def create_access_token(data: Dict[str, Any]) -> str:
    """Generates a JWT access token using jwcrypto."""
    claims = data.copy()
    claims.update({
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp())
    })
    token = jwt.JWT(header={"alg": ALGORITHM}, claims=claims)
    token.make_signed_token(JWK_KEY)
    return token.serialize()

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and verifies a JWT access token using jwcrypto."""
    try:
        decoded_token = jwt.JWT(key=JWK_KEY, jwt=token)
        return json.loads(decoded_token.claims)
    except JWException:
        raise AuthError("Invalid token", status_code=401)
    except Exception:
        raise AuthError("Could not validate credentials", status_code=401)