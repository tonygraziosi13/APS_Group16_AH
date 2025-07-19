from UniChain.utils.validator import Validator


class OptionalActivity:
    """
    Rappresenta un'attività formativa opzionale svolta dallo studente,
    come un tirocinio, un progetto esterno o una mobilità.
    """

    def __init__(self, name: str, type_: str, duration: int):
        """
        Inizializza un'attività opzionale con nome, tipo e durata.
        Tutti i campi sono sottoposti a validazione tramite Validator.
        """
        self.name = Validator.validate_string(name, "name")
        self.type = Validator.validate_string(type_, "type")
        self.duration = Validator.validate_integer(duration, "duration")

    def to_dict(self):
        """
        Serializza l’attività opzionale in formato dizionario JSON-compatibile.
        """
        return {
            "name": self.name,
            "type": self.type,
            "duration": self.duration
        }

    def __repr__(self):
        return f"OptionalActivity({self.name}, {self.type}, {self.duration}h)"
