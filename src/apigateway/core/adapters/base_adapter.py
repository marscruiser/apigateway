# Abstract base class for framework adapters
from abc import ABC,abstractmethod
from typing import Dict,Any
from apigateway.exceptions.GatewayValidationError import GatewayValidationError
from abc import ABC, abstractmethod
from typing import Any, Dict


class FrameworkAdapter(ABC):
    """Abstract adapter for different web frameworks"""
    
    @abstractmethod
    def extract_request_data(self, *args, **kwargs) -> Dict[str, Any]:
        """Extract request data from framework-specific request object"""
        pass
    
    @abstractmethod
    def handle_validation_error(self, error: GatewayValidationError) -> Any:
        """Handle validation error in framework-specific way"""
        pass
        
        # ... (existing methods: extract_request_data, handle_validation_error) ...

    @abstractmethod
    def get_auth_header(self, *args, **kwargs) -> str | None:
        """Extracts the Authorization header from the request."""
        pass

    @abstractmethod
    def handle_auth_error(self, error: Any) -> Any:
        """Returns a framework-specific authentication error response."""
        pass
