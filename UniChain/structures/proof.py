from datetime import datetime, UTC


class Proof:
    """
    Rappresenta una prova crittografica (firma digitale) associata alla credenziale accademica.
    Segue il formato delle Verifiable Credentials.
    """

    def __init__(self, signature_value: str, verification_method: str = "RSA_SHA256"):
        """
        Inizializza un oggetto Proof con valore della firma e metodo di verifica.
        Imposta automaticamente il timestamp corrente (UTC) e il tipo di firma.
        """
        self.type = "DigitalSignature"
        self.created = datetime.now(UTC).isoformat()
        self.verification_method = verification_method
        self.signature_value = signature_value

    def to_dict(self):
        """
        Converte l'oggetto Proof in un dizionario JSON-compatibile.
        """
        return {
            "type": self.type,
            "created": self.created,
            "verificationMethod": self.verification_method,
            "signatureValue": self.signature_value  # ✅ corretto typo
        }

    def __repr__(self):
        return f"Proof({self.verification_method}, created={self.created})"
