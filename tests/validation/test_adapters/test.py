from flask import Flask
from pydantic import BaseModel, ConfigDict
from apigateway.core.enums.validation_modes import ValidationMode
from apigateway.core.validation import validate_flask, PreValidators

app = Flask(__name__)

# --- SCHEMAS ---

class UserSchema(BaseModel):
    username: str
    age: int
    email: str
    model_config = ConfigDict(extra="forbid")

class ContactSchema(BaseModel):
    name: str
    email: str
    message: str
    model_config = ConfigDict(extra="forbid")

class SearchSchema(BaseModel):
    query: str
    limit: int = 10
    category: str = "all"
    model_config = ConfigDict(extra="forbid")

# --- ENDPOINTS ---

@app.route('/users', methods=['POST'])
@validate_flask(UserSchema, mode=ValidationMode.STRICT)
def create_user(validated: UserSchema):
    """Create a new user - JSON body required"""
    return {
        "success": True,
        "message": f"User {validated.username} created successfully",
        "user": {
            "username": validated.username,
            "age": validated.age,
            "email": validated.email
        }
    }

@app.route('/contact', methods=['POST'])
@validate_flask(
    ContactSchema,
    mode=ValidationMode.LAX,
    pre_validators=[PreValidators.normalize_email, PreValidators.sanitize_strings]
)
def submit_contact(validated: ContactSchema):
    """Submit contact form - handles form data or JSON"""
    return {
        "success": True,
        "message": "Contact form submitted",
        "data": {
            "name": validated.name,
            "email": validated.email,
            "message": validated.message
        }
    }

@app.route('/search', methods=['GET'])
@validate_flask(SearchSchema, mode=ValidationMode.LAX)
def search(validated: SearchSchema):
    """Search with query parameters"""
    return {
        "success": True,
        "query": validated.query,
        "limit": validated.limit,
        "category": validated.category,
        "results": f"Found results for '{validated.query}' in {validated.category}"
    }

@app.route('/mixed', methods=['POST'])
@validate_flask(UserSchema, mode=ValidationMode.LAX)
def mixed_data(validated: UserSchema):
    """Combines JSON body + query parameters"""
    return {
        "success": True,
        "message": "Mixed data processed",
        "user": validated.dict()
    }

# Custom post-validator example
def uppercase_username(user: UserSchema) -> UserSchema:
    user.username = user.username.upper()
    return user

@app.route('/users/premium', methods=['POST'])
@validate_flask(UserSchema, post_validators=[uppercase_username])
def create_premium_user(validated: UserSchema):
    """Create premium user with uppercase username"""
    return {
        "success": True,
        "message": f"Premium user {validated.username} created",
        "user": validated.dict()
    }

@app.route('/', methods=['GET'])
def home():
    """API documentation"""
    return {
        "message": "API Gateway Flask Example",
        "endpoints": {
            "POST /users": "Create user (JSON: username, age, email)",
            "POST /contact": "Submit contact form (JSON/form: name, email, message)",
            "GET /search": "Search (query params: query, limit?, category?)",
            "POST /mixed": "Mixed data (JSON body + query params)",
            "POST /users/premium": "Create premium user (uppercase username)"
        },
        "test_examples": {
            "create_user": "curl -X POST http://localhost:5000/users -H 'Content-Type: application/json' -d '{\"username\":\"alice\",\"age\":25,\"email\":\"alice@example.com\"}'",
            "search": "curl 'http://localhost:5000/search?query=python&limit=5&category=tutorials'",
            "contact_form": "curl -X POST http://localhost:5000/contact -d 'name=Bob&email=BOB@TEST.COM&message=Hello world'",
            "mixed_data": "curl -X POST 'http://localhost:5000/mixed?age=30' -H 'Content-Type: application/json' -d '{\"username\":\"charlie\",\"email\":\"charlie@test.com\"}'"
        }
    }

if __name__ == '__main__':
    print("🚀 Starting Flask API Gateway Example...")
    print("📍 Open http://localhost:5000 for documentation and test commands")
    print("🔧 Try the curl commands shown in the response!")
    app.run(debug=True, host='0.0.0.0', port=5000)