import sys
import os
# This path modification is no longer needed if you ran `pip install -e .`
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, jsonify
from pydantic import BaseModel, Extra
from auth import require_flask_auth
from auth_utils import create_access_token
# This is the line to change 👇
from apigateway.core.validation import validate_flask

app = Flask(__name__)

# --- Mock User Database ---
users_db = {
    "testuser": {"password": "password123", "user_id": 1, "role": "user"}
}

# --- Pydantic Models ---
class LoginSchema(BaseModel, extra=Extra.forbid):
    username: str
    password: str

class ProtectedDataSchema(BaseModel, extra=Extra.forbid):
    important_data: str

# --- Endpoints ---
@app.route("/login", methods=["POST"])
@validate_flask(LoginSchema)
def login(validated: LoginSchema):
    user = users_db.get(validated.username)
    if not user or user["password"] != validated.password:
        return jsonify({"detail": "Invalid username or password"}), 401
    
    token_payload = {"sub": user["user_id"], "role": user["role"]}
    access_token = create_access_token(data=token_payload)
    
    return jsonify({"access_token": access_token, "token_type": "bearer"})


@app.route("/profile", methods=["GET"])
@require_flask_auth()
def get_profile(user_payload: dict):
    return jsonify({
        "message": f"Welcome user ID {user_payload.get('sub')}!",
        "role": user_payload.get('role'),
        "token_expires_at": user_payload.get('exp')
    })


@app.route("/submit", methods=["POST"])
@require_flask_auth()
@validate_flask(ProtectedDataSchema)
def submit_protected_data(validated: ProtectedDataSchema, user_payload: dict):
    user_id = user_payload.get('sub')
    print(f"User {user_id} submitted data: {validated.important_data}")
    
    return jsonify({
        "status": "success",
        "message": f"User {user_id} successfully submitted data.",
        "received_data": validated.model_dump()
    })

if __name__ == "__main__":
    app.run(debug=True)