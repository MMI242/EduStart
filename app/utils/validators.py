import re
from typing import Optional
from datetime import datetime


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    return True, None


def validate_child_age(age: int, min_age: int = 4, max_age: int = 10) -> bool:
    """Validate child age is within acceptable range"""
    return min_age <= age <= max_age


def validate_difficulty_level(level: int) -> bool:
    """Validate difficulty level is between 1 and 10"""
    return 1 <= level <= 10


def sanitize_string(text: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_date_range(
    start_date: datetime,
    end_date: datetime
) -> tuple[bool, Optional[str]]:
    """
    Validate date range
    Returns (is_valid, error_message)
    """
    if start_date > end_date:
        return False, "Start date must be before end date"
    
    if end_date > datetime.utcnow():
        return False, "End date cannot be in the future"
    
    # Check if range is too large (e.g., more than 1 year)
    days_diff = (end_date - start_date).days
    if days_diff > 365:
        return False, "Date range cannot exceed 1 year"
    
    return True, None