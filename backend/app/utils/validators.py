import re

from marshmallow import ValidationError

PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")


def validate_password_strength(password):
    if not PASSWORD_PATTERN.match(password):
        raise ValidationError(
            "Password must be at least 8 characters and include uppercase, lowercase, and a number."
        )


def sanitize_text(value):
    if value is None:
        return None
    return value.strip()
