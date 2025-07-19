from UniChain.utils.validator import Validator


class Issuer:
    """
    Rappresenta l'ente che emette la credenziale accademica.
    Include identificativo interno, nome ufficiale e località.
    """

    def __init__(self, issuer_id: str, name: str, location: str):
        """
        Inizializza l'emittente con ID, nome e sede.
        Tutti i campi sono sottoposti a validazione tramite Validator.
        """
        self.id = Validator.validate_string(issuer_id, "id")
        self.name = Validator.validate_only_char(name, "name")
        self.location = Validator.validate_only_char(location, "location")

    def to_dict(self) -> dict:
        """
        Serializza l’oggetto Issuer in un dizionario JSON-compatibile.
        """
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location
        }

    def __repr__(self):
        return f"Issuer({self.id}, {self.name}, {self.location})"
