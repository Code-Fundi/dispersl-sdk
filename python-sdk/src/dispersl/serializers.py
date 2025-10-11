"""
Request/response serialization utilities.

This module handles serialization and deserialization of data
for API requests and responses, including datetime handling,
null/undefined values, and nested object validation.
"""

import json
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ValidationError as PydanticValidationError


class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles datetime objects.
    
    Converts datetime objects to ISO 8601 format strings.
    """
    
    def default(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, 'dict'):  # Pydantic models
            return obj.dict()
        elif hasattr(obj, '__dict__'):  # Custom objects
            return obj.__dict__
        
        return super().default(obj)


def serialize_request_data(data: Any) -> Dict[str, Any]:
    """
    Serialize request data for API calls.
    
    Handles:
    - Pydantic models -> dict
    - Datetime objects -> ISO 8601 strings
    - None values -> null
    - Custom objects -> dict representation
    
    Args:
        data: Data to serialize
    
    Returns:
        Serialized data as dictionary
    
    Raises:
        SerializationError: If serialization fails
    """
    try:
        if data is None:
            return {}
        
        if isinstance(data, dict):
            return data
        
        if isinstance(data, BaseModel):
            return data.dict(exclude_none=True)
        
        if hasattr(data, '__dict__'):
            return data.__dict__
        
        # For other types, try JSON serialization
        json_str = json.dumps(data, cls=DateTimeEncoder)
        return json.loads(json_str)
    
    except (TypeError, ValueError, PydanticValidationError) as e:
        from .exceptions import SerializationError
        raise SerializationError(f"Failed to serialize request data: {e}", original_error=e)


def deserialize_response_data(
    response_data: Union[str, bytes, Dict[str, Any]],
    model_class: Optional[type] = None,
) -> Any:
    """
    Deserialize response data from API calls.
    
    Handles:
    - JSON strings/bytes -> Python objects
    - Datetime strings -> datetime objects
    - Model validation with Pydantic
    
    Args:
        response_data: Raw response data
        model_class: Optional Pydantic model class for validation
    
    Returns:
        Deserialized data
    
    Raises:
        SerializationError: If deserialization fails
    """
    try:
        # Parse JSON if needed
        if isinstance(response_data, (str, bytes)):
            if isinstance(response_data, bytes):
                response_data = response_data.decode('utf-8')
            data = json.loads(response_data)
        else:
            data = response_data
        
        # Validate with Pydantic model if provided
        if model_class and issubclass(model_class, BaseModel):
            if isinstance(data, list):
                return [model_class(**item) for item in data]
            elif isinstance(data, dict):
                return model_class(**data)
            else:
                return model_class(data)
        
        return data
    
    except (json.JSONDecodeError, ValueError, PydanticValidationError) as e:
        from .exceptions import SerializationError
        raise SerializationError(f"Failed to deserialize response data: {e}", original_error=e)


def serialize_datetime(obj: datetime) -> str:
    """
    Serialize datetime object to ISO 8601 string.
    
    Args:
        obj: Datetime object to serialize
    
    Returns:
        ISO 8601 formatted string
    """
    return obj.isoformat()


def deserialize_datetime(date_string: str) -> datetime:
    """
    Deserialize ISO 8601 string to datetime object.
    
    Args:
        date_string: ISO 8601 formatted string
    
    Returns:
        Datetime object
    
    Raises:
        SerializationError: If parsing fails
    """
    try:
        # Handle various ISO 8601 formats
        if 'T' in date_string:
            # Full datetime
            if date_string.endswith('Z'):
                date_string = date_string[:-1] + '+00:00'
            return datetime.fromisoformat(date_string)
        else:
            # Date only
            return datetime.fromisoformat(date_string + 'T00:00:00')
    
    except ValueError as e:
        from .exceptions import SerializationError
        raise SerializationError(f"Failed to parse datetime: {date_string}", original_error=e)


def clean_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove None values from dictionary recursively.
    
    Args:
        data: Dictionary to clean
    
    Returns:
        Dictionary with None values removed
    """
    if not isinstance(data, dict):
        return data
    
    cleaned = {}
    for key, value in data.items():
        if value is None:
            continue
        elif isinstance(value, dict):
            cleaned_value = clean_none_values(value)
            if cleaned_value:  # Only add if not empty after cleaning
                cleaned[key] = cleaned_value
        elif isinstance(value, list):
            cleaned_list = [clean_none_values(item) if isinstance(item, dict) else item for item in value]
            cleaned_list = [item for item in cleaned_list if item is not None]
            if cleaned_list:  # Only add if not empty after cleaning
                cleaned[key] = cleaned_list
        else:
            cleaned[key] = value
    
    return cleaned


def validate_required_fields(
    data: Dict[str, Any],
    required_fields: List[str],
    context: str = "request",
) -> None:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Data to validate
        required_fields: List of required field names
        context: Context for error messages
    
    Raises:
        ValidationError: If required fields are missing
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        from .exceptions import ValidationError
        raise ValidationError(
            f"Missing required fields in {context}: {', '.join(missing_fields)}"
        )


def convert_camel_to_snake(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert camelCase keys to snake_case recursively.
    
    Args:
        data: Dictionary with camelCase keys
    
    Returns:
        Dictionary with snake_case keys
    """
    if not isinstance(data, dict):
        return data
    
    converted = {}
    for key, value in data.items():
        # Convert camelCase to snake_case
        snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
        
        # Recursively convert nested dictionaries
        if isinstance(value, dict):
            converted[snake_key] = convert_camel_to_snake(value)
        elif isinstance(value, list):
            converted[snake_key] = [
                convert_camel_to_snake(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            converted[snake_key] = value
    
    return converted


def convert_snake_to_camel(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert snake_case keys to camelCase recursively.
    
    Args:
        data: Dictionary with snake_case keys
    
    Returns:
        Dictionary with camelCase keys
    """
    if not isinstance(data, dict):
        return data
    
    converted = {}
    for key, value in data.items():
        # Convert snake_case to camelCase
        camel_key = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(key.split('_')))
        
        # Recursively convert nested dictionaries
        if isinstance(value, dict):
            converted[camel_key] = convert_snake_to_camel(value)
        elif isinstance(value, list):
            converted[camel_key] = [
                convert_snake_to_camel(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            converted[camel_key] = value
    
    return converted
