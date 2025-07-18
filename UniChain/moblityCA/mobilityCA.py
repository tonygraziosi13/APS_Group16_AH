# File: UniChain/mobilityCA/mobilityCA.py

from cryptography.hazmat.primitives.asymmetric import rsa
from certificate_manager import CertificateManager


class MobilityCA:
    def __init__(self):
        # 1. Genera coppia di chiavi (PKI)
        self._private_key = self._generate_private_key()
        self._public_key = self._private_key.public_key()

        # 2. Inizializza il gestore dei certificati
        self._certificate_manager = CertificateManager(
            private_key=self._private_key,
            public_key=self._public_key
        )

    def _generate_private_key(self):
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # --- Metodi pubblici per interfaccia con University ---

    def issue_certificate(self, public_key, university_id, official_name, university_code, location):
        return self._certificate_manager.issue_certificate(
            public_key=public_key,
            university_id=university_id,
            official_name=official_name,
            university_code=university_code,
            location=location
        )

    def revoke_certificate(self, university_id):
        return self._certificate_manager.revoke_certificate(university_id)

    def is_certificate_revoked(self, certificate):
        return self._certificate_manager.is_certificate_revoked(certificate)

    def get_root_certificate(self):
        return self._certificate_manager.get_root_cert()
