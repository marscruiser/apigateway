from dotenv import load_dotenv
load_dotenv() # Loads the .env file at the very beginning

from flask import Flask, jsonify
from pydantic import BaseModel, ConfigDict
# We import all three decorators/helpers for different access levels
from auth import require_flask_token, require_flask_access
from auth_utils import create_access_token
# We import all validation helpers
from apigateway.core.enums.validation_modes import ValidationMode
from apigateway.core.validation import validate_flask, PreValidators

app = Flask(__name__)

# --- MOCK USER DATABASE (for login) ---
users_db = {
    "testuser": {"password": "password123", "user_id": 1, "role": "admin"} # Made this user an admin for testing
}

# --- SCHEMAS (ALL Pydantic Models) ---

class LoginSchema(BaseModel):
    username: str
    password: str
    model_config = ConfigDict(extra='forbid')

class ProtectedDataSchema(BaseModel):
    important_data: str
    model_config = ConfigDict(extra='forbid')

class UserSchema(BaseModel):
    username: str
    age: int
    email: str
    model_config = ConfigDict(extra='forbid')

class ContactSchema(BaseModel):
    name: str
    email: str
    message: str
    model_config = ConfigDict(extra='forbid')

class SearchSchema(BaseModel):
    query: str
    limit: int = 10
    category: str = "all"
    model_config = ConfigDict(extra='forbid')

# --- HELPER FUNCTIONS (POST-VALIDATORS) ---

def uppercase_username(user: UserSchema) -> UserSchema:
    """A custom post-validator to transform data after validation."""
    user.username = user.username.upper()
    return user

# --- ENDPOINTS ---

@app.route('/', methods=['GET'])
def home():
    """API documentation and root endpoint for all merged features."""
    return jsonify({
        "message": "API Gateway: Full Example with Validation and Role-Based Auth",
        "public_endpoints": {
            "POST /login": "Get a JWT access token.",
            "POST /contact": "Submit a public contact form.",
            "GET /search": "Perform a public search."
        },
        "protected_endpoints (any logged-in user)": {
            "GET /profile": "View your profile using any valid token.",
            "POST /submit": "Submit generic protected data.",
            "POST /mixed": "Submit mixed data (JSON + query params)."
        },
        "protected_endpoints (admin role required)": {
            "POST /users": "Create a new user.",
            "POST /users/premium": "Create a premium user."
        }
    })

# --- Public Endpoints ---

@app.route("/login", methods=["POST"])
@validate_flask(LoginSchema)
def login(validated: LoginSchema):
    """Login endpoint. Validates credentials and returns a JWT access token."""
    user = users_db.get(validated.username)
    if not user or user["password"] != validated.password:
        return jsonify({"detail": "Invalid username or password"}), 401
    token_payload = {"sub": user["user_id"], "role": user["role"]}
    access_token = create_access_token(data=token_payload)
    return jsonify({"access_token": access_token, "token_type": "bearer"})

@app.route('/contact', methods=['POST'])
@validate_flask(ContactSchema, mode=ValidationMode.LAX, pre_validators=[PreValidators.normalize_email, PreValidators.sanitize_strings])
def submit_contact(validated: ContactSchema):
    """Submit contact form - public and uses pre-validators."""
    return {"success": True, "message": "Contact form submitted", "data": validated.model_dump()}

@app.route('/search', methods=['GET'])
@validate_flask(SearchSchema, mode=ValidationMode.LAX)
def search(validated: SearchSchema):
    """Search with query parameters - public."""
    return {"success": True, "query": validated.query, "limit": validated.limit, "category": validated.category}


# --- Protected Endpoints (Any Logged-in User) ---

@app.route("/profile", methods=["GET"])
@require_flask_token()
def get_profile(user_payload: dict):
    """A protected endpoint accessible by any authenticated user."""
    return jsonify({"message": "You can see this because you are logged in.", "your_user_data": user_payload})

@app.route("/submit", methods=["POST"])
@require_flask_token()
@validate_flask(ProtectedDataSchema)
def submit_protected_data(validated: ProtectedDataSchema, user_payload: dict):
    """A protected endpoint that validates submitted data."""
    return jsonify({"status": "success", "message": "Generic data submitted.", "received_data": validated.model_dump()})

@app.route('/mixed', methods=['POST'])
@require_flask_token()
@validate_flask(UserSchema, mode=ValidationMode.LAX)
def mixed_data(validated: UserSchema, user_payload: dict):
    """Combines JSON body + query parameters - requires any valid token."""
    return {"success": True, "message": "Mixed data processed", "user": validated.model_dump()}


# --- Protected Endpoints (Admin Role Required) ---

@app.route('/users', methods=['POST'])
@require_flask_access(allowed_roles=['admin'])
@validate_flask(UserSchema, mode=ValidationMode.STRICT)
def create_user(validated: UserSchema, user_payload: dict):
    """Create a new user - requires an admin role."""
    return {"success": True, "message": f"User {validated.username} created by admin.", "user": validated.model_dump()}

@app.route('/users/premium', methods=['POST'])
@require_flask_access(allowed_roles=['admin'])
@validate_flask(UserSchema, post_validators=[uppercase_username])
def create_premium_user(validated: UserSchema, user_payload: dict):
    """Create a premium user with a post-validator - requires an admin role."""
    return {"success": True, "message": f"Premium user {validated.username} created by admin.", "user": validated.model_dump()}


# --- Server Start ---
if __name__ == '__main__':
    print("🚀 Starting Complete Flask API...")
    print("📍 Listening on http://127.0.0.1:5001")
    app.run(debug=True, host='127.0.0.1', port=5001)