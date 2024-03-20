import re
def validate_password(password):
    # Validate password length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    # Validate password complexity (at least 1 uppercase, 1 lowercase, 1 number, and 1 special character)
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit (number)."
    if not re.search(r"[!@#$%^&*()-_=+{};:,<.>]", password):
        return False, "Password must contain at least one special character."

    return True, "Password is valid."