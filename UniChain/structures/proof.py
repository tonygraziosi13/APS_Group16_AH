from datetime import datetime, UTC


class Proof:
    def __init__(self, signature_value: str, verification_method: str = "RSA_SHA256"):
        self.type = "DigitalSignature"
        self.created = datetime.now(UTC).isoformat()
        self.verification_method = verification_method
        self.signature_value = signature_value

    def to_dict(self):
        return {
            "type": self.type,
            "created": self.created,
            "verificationMethod": self.verification_method,
            "singatureValue": self.signature_value
        }
