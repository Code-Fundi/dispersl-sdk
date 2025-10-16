"""Comprehensive unit tests for serializers module."""

import json
from datetime import datetime, date
from decimal import Decimal
import pytest
from pydantic import BaseModel, Field
from dispersl.serializers import (
    DateTimeEncoder,
    serialize_request_data,
    deserialize_response_data,
    serialize_datetime,
    deserialize_datetime,
    clean_none_values,
    validate_required_fields,
    convert_camel_to_snake,
    convert_snake_to_camel,
)
from dispersl.exceptions import SerializationError, ValidationError


class TestDateTimeEncoder:
    """Test DateTimeEncoder functionality."""

    def test_encode_datetime(self):
        """Test encoding datetime objects."""
        dt = datetime(2025, 1, 10, 12, 30, 45)
        encoder = DateTimeEncoder()
        result = json.dumps({"timestamp": dt}, cls=DateTimeEncoder)
        assert dt.isoformat() in result

    def test_encode_date(self):
        """Test encoding date objects."""
        d = date(2025, 1, 10)
        result = json.dumps({"date": d}, cls=DateTimeEncoder)
        assert "2025-01-10" in result

    def test_encode_decimal(self):
        """Test encoding Decimal objects."""
        dec = Decimal("123.45")
        result = json.dumps({"amount": dec}, cls=DateTimeEncoder)
        parsed = json.loads(result)
        assert parsed["amount"] == 123.45


class TestSerializeRequestData:
    """Test serialize_request_data function."""

    def test_serialize_dict(self):
        """Test serializing a dictionary."""
        data = {"key": "value", "number": 42}
        result = serialize_request_data(data)
        assert result == data

    def test_serialize_none(self):
        """Test serializing None returns empty dict."""
        result = serialize_request_data(None)
        assert result == {}

    def test_serialize_pydantic_model(self):
        """Test serializing Pydantic models."""
        class TestModel(BaseModel):
            name: str
            age: int
            optional: str | None = None

        model = TestModel(name="Test", age=30)
        result = serialize_request_data(model)
        assert result == {"name": "Test", "age": 30}
        assert "optional" not in result  # exclude_none

    def test_serialize_datetime(self):
        """Test serializing datetime in dict."""
        dt = datetime(2025, 1, 10, 12, 30)
        data = {"timestamp": dt}
        result = serialize_request_data(data)
        # Should still have datetime object in dict
        assert isinstance(result["timestamp"], datetime)

    def test_serialize_custom_object(self):
        """Test serializing custom objects."""
        class CustomObj:
            def __init__(self):
                self.field1 = "value1"
                self.field2 = 42

        obj = CustomObj()
        result = serialize_request_data(obj)
        assert result == {"field1": "value1", "field2": 42}


class TestDeserializeResponseData:
    """Test deserialize_response_data function."""

    def test_deserialize_json_string(self):
        """Test deserializing JSON string."""
        json_str = '{"key": "value", "number": 42}'
        result = deserialize_response_data(json_str)
        assert result == {"key": "value", "number": 42}

    def test_deserialize_bytes(self):
        """Test deserializing bytes."""
        json_bytes = b'{"key": "value"}'
        result = deserialize_response_data(json_bytes)
        assert result == {"key": "value"}

    def test_deserialize_dict(self):
        """Test deserializing dict returns as-is."""
        data = {"key": "value"}
        result = deserialize_response_data(data)
        assert result == data

    def test_deserialize_with_model(self):
        """Test deserializing with Pydantic model."""
        class TestModel(BaseModel):
            name: str
            age: int

        json_str = '{"name": "Test", "age": 30}'
        result = deserialize_response_data(json_str, TestModel)
        assert isinstance(result, TestModel)
        assert result.name == "Test"
        assert result.age == 30

    def test_deserialize_list_with_model(self):
        """Test deserializing list with Pydantic model."""
        class TestModel(BaseModel):
            id: int
            name: str

        data = [{"id": 1, "name": "First"}, {"id": 2, "name": "Second"}]
        result = deserialize_response_data(data, TestModel)
        assert len(result) == 2
        assert all(isinstance(item, TestModel) for item in result)
        assert result[0].id == 1
        assert result[1].name == "Second"

    def test_deserialize_invalid_json(self):
        """Test deserializing invalid JSON raises error."""
        with pytest.raises(SerializationError):
            deserialize_response_data("{invalid json")


class TestSerializeDeserializeDatetime:
    """Test datetime serialization/deserialization functions."""

    def test_serialize_datetime(self):
        """Test serializing datetime to ISO string."""
        dt = datetime(2025, 1, 10, 12, 30, 45)
        result = serialize_datetime(dt)
        assert result == dt.isoformat()

    def test_deserialize_datetime(self):
        """Test deserializing ISO datetime string."""
        dt_str = "2025-01-10T12:30:45"
        result = deserialize_datetime(dt_str)
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 10

    def test_deserialize_datetime_with_z(self):
        """Test deserializing datetime with Z timezone."""
        dt_str = "2025-01-10T12:30:45Z"
        result = deserialize_datetime(dt_str)
        assert isinstance(result, datetime)

    def test_deserialize_date_only(self):
        """Test deserializing date string."""
        date_str = "2025-01-10"
        result = deserialize_datetime(date_str)
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 10

    def test_deserialize_invalid_datetime(self):
        """Test deserializing invalid datetime raises error."""
        with pytest.raises(SerializationError):
            deserialize_datetime("not-a-date")


class TestCleanNoneValues:
    """Test clean_none_values function."""

    def test_clean_simple_dict(self):
        """Test cleaning simple dict with None values."""
        data = {"key1": "value", "key2": None, "key3": 42}
        result = clean_none_values(data)
        assert result == {"key1": "value", "key3": 42}
        assert "key2" not in result

    def test_clean_nested_dict(self):
        """Test cleaning nested dict with None values."""
        data = {
            "level1": {
                "key1": "value",
                "key2": None,
                "nested": {
                    "key3": None,
                    "key4": "test"
                }
            },
            "key5": None
        }
        result = clean_none_values(data)
        assert "key5" not in result
        assert "key2" not in result["level1"]
        assert "key3" not in result["level1"]["nested"]
        assert result["level1"]["nested"]["key4"] == "test"

    def test_clean_list_with_none(self):
        """Test cleaning list containing None values."""
        data = {"items": [1, None, 2, None, 3]}
        result = clean_none_values(data)
        assert result["items"] == [1, 2, 3]

    def test_clean_list_of_dicts(self):
        """Test cleaning list of dicts with None values."""
        data = {
            "items": [
                {"id": 1, "name": "First", "optional": None},
                {"id": 2, "name": "Second", "optional": "value"}
            ]
        }
        result = clean_none_values(data)
        assert "optional" not in result["items"][0]
        assert result["items"][1]["optional"] == "value"

    def test_clean_non_dict(self):
        """Test cleaning non-dict returns as-is."""
        data = "not a dict"
        result = clean_none_values(data)
        assert result == data


class TestValidateRequiredFields:
    """Test validate_required_fields function."""

    def test_validate_all_fields_present(self):
        """Test validation passes when all required fields present."""
        data = {"field1": "value1", "field2": "value2", "field3": 42}
        # Should not raise any exception
        validate_required_fields(data, ["field1", "field2"])

    def test_validate_missing_fields(self):
        """Test validation fails when required fields missing."""
        data = {"field1": "value1"}
        with pytest.raises(ValidationError) as exc_info:
            validate_required_fields(data, ["field1", "field2", "field3"])
        
        assert "field2" in str(exc_info.value)
        assert "field3" in str(exc_info.value)

    def test_validate_none_value(self):
        """Test validation fails when required field is None."""
        data = {"field1": "value1", "field2": None}
        with pytest.raises(ValidationError):
            validate_required_fields(data, ["field1", "field2"])

    def test_validate_with_context(self):
        """Test validation error includes context."""
        data = {"field1": "value1"}
        with pytest.raises(ValidationError) as exc_info:
            validate_required_fields(data, ["field2"], context="login request")
        
        assert "login request" in str(exc_info.value)


class TestConvertCamelToSnake:
    """Test convert_camel_to_snake function."""

    def test_convert_simple_keys(self):
        """Test converting simple camelCase keys."""
        data = {"firstName": "John", "lastName": "Doe", "age": 30}
        result = convert_camel_to_snake(data)
        assert result == {"first_name": "John", "last_name": "Doe", "age": 30}

    def test_convert_nested_dict(self):
        """Test converting nested dictionaries."""
        data = {
            "userId": 123,
            "userInfo": {
                "firstName": "John",
                "lastName": "Doe"
            }
        }
        result = convert_camel_to_snake(data)
        assert result["user_id"] == 123
        assert result["user_info"]["first_name"] == "John"

    def test_convert_list_of_dicts(self):
        """Test converting list of dictionaries."""
        data = {
            "userList": [
                {"userId": 1, "userName": "First"},
                {"userId": 2, "userName": "Second"}
            ]
        }
        result = convert_camel_to_snake(data)
        assert result["user_list"][0]["user_id"] == 1
        assert result["user_list"][1]["user_name"] == "Second"

    def test_convert_non_dict(self):
        """Test converting non-dict returns as-is."""
        data = "not a dict"
        result = convert_camel_to_snake(data)
        assert result == data


class TestConvertSnakeToCamel:
    """Test convert_snake_to_camel function."""

    def test_convert_simple_keys(self):
        """Test converting simple snake_case keys."""
        data = {"first_name": "John", "last_name": "Doe", "age": 30}
        result = convert_snake_to_camel(data)
        assert result == {"firstName": "John", "lastName": "Doe", "age": 30}

    def test_convert_nested_dict(self):
        """Test converting nested dictionaries."""
        data = {
            "user_id": 123,
            "user_info": {
                "first_name": "John",
                "last_name": "Doe"
            }
        }
        result = convert_snake_to_camel(data)
        assert result["userId"] == 123
        assert result["userInfo"]["firstName"] == "John"

    def test_convert_list_of_dicts(self):
        """Test converting list of dictionaries."""
        data = {
            "user_list": [
                {"user_id": 1, "user_name": "First"},
                {"user_id": 2, "user_name": "Second"}
            ]
        }
        result = convert_snake_to_camel(data)
        assert result["userList"][0]["userId"] == 1
        assert result["userList"][1]["userName"] == "Second"

    def test_convert_non_dict(self):
        """Test converting non-dict returns as-is."""
        data = "not a dict"
        result = convert_snake_to_camel(data)
        assert result == data

    def test_round_trip_conversion(self):
        """Test converting camel to snake and back."""
        original = {"firstName": "John", "lastName": "Doe"}
        snake = convert_camel_to_snake(original)
        camel = convert_snake_to_camel(snake)
        assert camel == original


class TestSerializationError:
    """Test SerializationError exception."""

    def test_create_error(self):
        """Test creating SerializationError."""
        error = SerializationError("Test error")
        assert str(error) == "Test error"

    def test_error_with_cause(self):
        """Test SerializationError with cause."""
        original = ValueError("Original error")
        try:
            raise SerializationError("Serialization failed") from original
        except SerializationError as error:
            assert error.__cause__ == original

    def test_error_in_context(self):
        """Test raising SerializationError in context."""
        with pytest.raises(SerializationError) as exc_info:
            raise SerializationError("Context error")
        
        assert "Context error" in str(exc_info.value)
