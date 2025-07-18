from ..utils.validator import Validator


class OptionalActivity:
    def __init__(self, name: str, type_: str, duration: int):
        self.name = Validator.validate_string(name, "name")
        self.type = Validator.validate_string(type_, "type")
        self.duration = Validator.validate_integer(duration, "duration")

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "duration": self.duration
        }
