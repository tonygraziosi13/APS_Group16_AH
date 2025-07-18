from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


class University:
    def __init__(self, university_id, official_name, university_code, location, mobility_ca):
        self.university_id = university_id
        self.official_name = official_name
        self.university_code = university_code
        self.location = location
        self.mobility_ca = mobility_ca

        # Generate key pair
        self._private_key = self._generate_private_key()
        self._public_key = self._private_key.public_key()

        self._certificate = None
        self._root_cert = None

    @staticmethod
    def _generate_private_key():
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def get_public_key(self):
        return self._public_key

    def get_certificate(self):
        return self._certificate

    def request_accreditation(self):
        self._certificate, self._root_cert = self.mobility_ca.issue_certificate(
            public_key=self._public_key,
            university_id=self.university_id,
            official_name=self.official_name,
            university_code=self.university_code,
            location=self.location
        )
        print(f"[University] Certificato ricevuto per {self.university_id}")

    def sign_message(self, message: bytes) -> bytes:
        return self._private_key.sign(
            message,
            padding=padding.PKCS1v15(),
            algorithm=hashes.SHA256()
        )

    def get_serialized_public_key(self) -> str:
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

    def generate_revocation_request(self, reason: str) -> dict:
        message = f"REVOKE:{self.university_id}:{reason}".encode()
        signature = self.sign_message(message)
        return {
            "university_id": self.university_id,
            "reason": reason,
            "signature": signature,
            "message": message,
            "certificate": self._certificate
        }

