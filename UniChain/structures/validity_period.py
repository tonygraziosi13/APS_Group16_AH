from ..utils.validator import Validator


class ValidityPeriod:
    def __init__(self, issued_at: str, expires_at: str = None):
        self.issued_at = Validator.validate_datetime(issued_at, "issuedAt")
        self.expires_at = Validator.validate_datetime(expires_at, "expiresAt") if expires_at else None

    def to_dict(self):
        result = {
            "issuedAt": self.issued_at
        }
        if self.expires_at:
            result["expiresAt"] = self.expires_at
        return result
