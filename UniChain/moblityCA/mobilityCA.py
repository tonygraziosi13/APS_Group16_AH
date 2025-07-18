from cryptography.hazmat.primitives.asymmetric import rsa
from UniChain.moblityCA.certificate_manager import CertificateManager
from utils.validator import Validator


class MobilityCA:
    def __init__(self):
        self._private_key = self._generate_private_key()
        self._public_key = self._private_key.public_key()

        self._validator = Validator()
        self._certificate_manager = CertificateManager(
            private_key=self._private_key,
            public_key=self._public_key
        )

    def _generate_private_key(self):
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # --- API per le Università ---

    def issue_certificate(self, public_key, university_id, official_name, university_code, location):
        # Validazione dei parametri fondamentali
        self._validator.validate_string(university_id, "university_id")
        self._validator.validate_only_char(official_name, "official_name")
        self._validator.validate_string(university_code, "university_code")
        self._validator.validate_only_char(location, "location")

        return self._certificate_manager.issue_certificate(
            public_key=public_key,
            university_id=university_id,
            official_name=official_name,
            university_code=university_code,
            location=location
        )

    def revoke_certificate(self, university_id):
        self._validator.validate_string(university_id, "university_id")
        return self._certificate_manager.revoke_certificate(university_id)

    def is_certificate_revoked(self, certificate):
        return self._certificate_manager.is_certificate_revoked(certificate)

    def get_root_certificate(self):
        return self._certificate_manager.get_root_cert()

    def get_public_registry(self):
        return self._certificate_manager.get_public_registry()

    def verify_signature(self, message: bytes, signature: bytes, certificate) -> bool:
        return self._certificate_manager.verify_signature(message, signature, certificate)
