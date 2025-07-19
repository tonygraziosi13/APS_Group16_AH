from UniChain.utils.validator import Validator


class ValidityPeriod:
    """
    Rappresenta il periodo di validità della credenziale.
    Include data di emissione obbligatoria ed eventuale data di scadenza.
    """

    def __init__(self, issued_at: str, expires_at: str = None):
        """
        Inizializza un oggetto ValidityPeriod con data di emissione e (facoltativa) scadenza.
        Le date devono essere stringhe ISO 8601 validate.
        """
        self.issued_at = Validator.validate_datetime(issued_at, "issuedAt")
        self.expires_at = Validator.validate_datetime(expires_at, "expiresAt") if expires_at else None

    def to_dict(self):
        """
        Converte il periodo di validità in un dizionario JSON-compatibile.
        """
        result = {
            "issuedAt": self.issued_at
        }
        if self.expires_at:
            result["expiresAt"] = self.expires_at
        return result

    def __repr__(self):
        return f"ValidityPeriod(issuedAt={self.issued_at}, expiresAt={self.expires_at})"
