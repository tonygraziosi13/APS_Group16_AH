from utils.validator import Validator


class Issuer:
    def __init__(self, issuer_id: str, name: str, location: str):
        self.id = Validator.validate_string(issuer_id, "id")
        self.name = Validator.validate_only_char(name, "name")
        self.location = Validator.validate_only_char(location, "location")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location
        }

