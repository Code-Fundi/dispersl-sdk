"""
Helper utilities for the Dispersl SDK.

This module provides common utility functions used throughout the SDK
for data processing, validation, and other operations.
"""

import re
from typing import Any, Optional, Union
from urllib.parse import urlencode, urlparse


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        url: String to validate as URL

    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def build_url(base_url: str, path: str, params: Optional[dict[str, Any]] = None) -> str:
    """
    Build a complete URL from base URL, path, and query parameters.

    Args:
        base_url: Base URL (e.g., "https://api.example.com")
        path: Path component (e.g., "/users/123")
        params: Query parameters

    Returns:
        Complete URL string
    """
    # Ensure base_url doesn't end with slash and path starts with slash
    base_url = base_url.rstrip("/")
    path = path.lstrip("/")

    url = f"{base_url}/{path}" if path else base_url

    if params:
        # Filter out None values
        filtered_params = {k: v for k, v in params.items() if v is not None}
        if filtered_params:
            url += f"?{urlencode(filtered_params)}"

    return url


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    # Ensure it's not empty
    if not sanitized:
        sanitized = "file"

    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
        if ext:
            sanitized = name[: 255 - len(ext) - 1] + "." + ext
        else:
            sanitized = sanitized[:255]

    return sanitized


def deep_merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge two dictionaries, with dict2 values taking precedence.

    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def flatten_dict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
    """
    Flatten a nested dictionary using the specified separator.

    Args:
        data: Dictionary to flatten
        separator: Separator to use for nested keys

    Returns:
        Flattened dictionary
    """

    def _flatten(obj: Any, parent_key: str = "") -> dict[str, Any]:
        items = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                items.extend(_flatten(value, new_key).items())
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                items.extend(_flatten(value, new_key).items())
        else:
            items.append((parent_key, obj))

        return dict(items)

    return _flatten(data)


def unflatten_dict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
    """
    Unflatten a dictionary using the specified separator.

    Args:
        data: Flattened dictionary
        separator: Separator used for nested keys

    Returns:
        Unflattened dictionary
    """
    result = {}

    for key, value in data.items():
        keys = key.split(separator)
        current = result

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    return result


def chunk_list(items: list[Any], chunk_size: int) -> list[list[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def remove_none_values(data: dict[str, Any]) -> dict[str, Any]:
    """
    Remove None values from a dictionary recursively.

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
            cleaned_value = remove_none_values(value)
            if cleaned_value:  # Only add if not empty after cleaning
                cleaned[key] = cleaned_value
        elif isinstance(value, list):
            cleaned_list = [
                remove_none_values(item) if isinstance(item, dict) else item for item in value
            ]
            cleaned_list = [item for item in cleaned_list if item is not None]
            if cleaned_list:  # Only add if not empty after cleaning
                cleaned[key] = cleaned_list
        else:
            cleaned[key] = value

    return cleaned


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes value as human-readable string.

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if bytes_value == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(bytes_value)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to maximum length with optional suffix.

    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL.

    Args:
        url: URL to extract domain from

    Returns:
        Domain string or None if invalid URL
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def is_valid_email(email: str) -> bool:
    """
    Check if a string is a valid email address.

    Args:
        email: String to validate as email

    Returns:
        True if valid email, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def generate_request_id() -> str:
    """
    Generate a unique request ID.

    Returns:
        Unique request ID string
    """
    import uuid

    return str(uuid.uuid4())


def retry_after_to_seconds(retry_after: Union[str, int]) -> int:
    """
    Convert Retry-After header value to seconds.

    Args:
        retry_after: Retry-After header value

    Returns:
        Seconds to wait
    """
    if isinstance(retry_after, int):
        return retry_after

    if isinstance(retry_after, str):
        # Try to parse as integer first
        try:
            return int(retry_after)
        except ValueError:
            pass

        # Try to parse as HTTP date
        try:
            import datetime
            from email.utils import parsedate_to_datetime

            parsed_date = parsedate_to_datetime(retry_after)
            now = datetime.datetime.now(datetime.timezone.utc)
            return int((parsed_date - now).total_seconds())
        except Exception:
            pass

    # Default to 60 seconds if parsing fails
    return 60
