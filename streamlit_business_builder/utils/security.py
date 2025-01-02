import re
import html
from typing import Optional

class SecurityUtils:
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not isinstance(text, str):
            return ""
        # HTML escape
        text = html.escape(text)
        # Remove any potential script tags or suspicious patterns
        text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL | re.I)
        return text

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength
        Returns: (is_valid, error_message)
        """
        if len(password) < 12:
            return False, "Password must be at least 12 characters long"
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        return True, None

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_username(username: str) -> tuple[bool, Optional[str]]:
        """
        Validate username format
        Returns: (is_valid, error_message)
        """
        if len(username) < 4:
            return False, "Username must be at least 4 characters long"
        if not username.isalnum():
            return False, "Username must contain only letters and numbers"
        return True, None

    @staticmethod
    def rate_limit_key(username: str) -> str:
        """Generate a rate limit key for Redis"""
        return f"login_attempts:{username}" 