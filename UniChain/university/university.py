from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization


class University:
    """
    Rappresenta una università che partecipa al sistema UniChain.
    Può richiedere accreditamento, firmare messaggi e accedere al proprio certificato pubblico.
    """

    def __init__(self, university_id, official_name, university_code, location, mobility_ca):
        self.university_id = university_id
        self.official_name = official_name
        self.university_code = university_code
        self.location = location
        self.mobility_ca = mobility_ca

        # Chiave RSA privata/pubblica
        self._private_key = self._generate_private_key()
        self._public_key = self._private_key.public_key()

        # Certificati rilasciati da MobilityCA
        self._certificate = None
        self._root_cert = None

    @staticmethod
    def _generate_private_key():
        """
        Genera una chiave privata RSA a 2048 bit.
        """
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def request_accreditation(self):
        """
        Richiede l'accreditamento a MobilityCA.
        La CA emette un certificato firmato con root certificate.
        """
        self._certificate, self._root_cert = self.mobility_ca.issue_certificate(
            public_key=self._public_key,
            university_id=self.university_id,
            official_name=self.official_name,
            university_code=self.university_code,
            location=self.location
        )
        print(f"[University] Certificato ricevuto per {self.university_id}")

    def sign_message(self, message: bytes) -> bytes:
        """
        Firma un messaggio arbitrario usando la chiave privata dell’università.
        """
        return self._private_key.sign(
            message,
            padding=padding.PKCS1v15(),
            algorithm=hashes.SHA256()
        )

    def get_certificate(self):
        return self._certificate

    def get_public_key(self):
        return self._public_key

    def get_serialized_public_key(self) -> str:
        """
        Restituisce la chiave pubblica in formato PEM serializzato.
        """
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

    def __repr__(self):
        return f"University({self.university_id}, {self.university_code})"
