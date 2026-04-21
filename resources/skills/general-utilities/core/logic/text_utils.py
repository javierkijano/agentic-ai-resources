import re

def sanitize_filename(filename: str) -> str:
    """Removes invalid characters from a string to make it a safe filename."""
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)

def extract_urls(text: str) -> list[str]:
    """Extracts all HTTP/HTTPS URLs from a given text."""
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.findall(url_pattern, text)

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncates text to a maximum length, appending '...' if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
