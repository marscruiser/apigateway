from typing import Any, Dict
from flask import request, jsonify # Imports moved to the top
from apigateway.core.adapters.base_adapter import FrameworkAdapter
from apigateway.exceptions.GatewayValidationError import GatewayValidationError
from auth_utils import AuthError


class FlaskAdapter(FrameworkAdapter):
    """Adapter for Flask framework"""

    def extract_request_data(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Extracts data by combining JSON body, form data, and query parameters.
        The order of precedence is: JSON > Form > Query Args.
        """
        data = {}

        # 1. Query parameters (lowest priority)
        if request.args:
            for key in request.args:
                values = request.args.getlist(key)
                data[key] = values[0] if len(values) == 1 else values

        # 2. Form data (overwrites query params with same name)
        if request.form:
            for key in request.form:
                values = request.form.getlist(key)
                data[key] = values[0] if len(values) == 1 else values

        # 3. JSON body (highest priority)
        if request.is_json:
            try:
                json_data = request.get_json()
                if json_data:
                    data.update(json_data)
            except Exception:
                # If get_json fails, it means the body is not valid JSON
                raise GatewayValidationError("Invalid JSON format in request body", [])

        return data

    def handle_validation_error(self, error: GatewayValidationError) -> Any:
        """Handles Pydantic validation errors with a 422 status code."""
        response = jsonify({
            "message": error.message,
            "details": error.details
        })
        response.status_code = 422  # Use 422 for semantic validation errors
        return response

    def get_auth_header(self, *args, **kwargs) -> str | None:
        """Extracts the Authorization header from the Flask request."""
        return request.headers.get("Authorization")

    def handle_auth_error(self, error: AuthError) -> any:
        """Returns a JSON response for authentication errors."""
        response = jsonify({"detail": error.message})
        response.status_code = error.status_code
        return response
