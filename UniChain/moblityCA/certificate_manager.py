import datetime
from typing import List
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from utils.validator import Validator


class CertificateManager:
    def __init__(self, private_key, public_key):
        self._private_key = private_key
        self._public_key = public_key
        self._certificati_uni: List[dict] = []
        self._generate_root_cert()
        self._validator = Validator()

    def _generate_root_cert(self):
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IT"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MobilityCA"),
            x509.NameAttribute(NameOID.COMMON_NAME, "RootCA MobilityCA"),
        ])
        self.root_cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(self._public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now())
            .not_valid_after(datetime.datetime.now() + datetime.timedelta(days=3650))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(self._private_key, hashes.SHA256())
        )

    def get_root_cert(self):
        return self.root_cert

    def issue_certificate(self, public_key, university_id, official_name, university_code, location):
        # Validazione input
        self._validator.validate_string(university_id, "university_id")
        self._validator.validate_only_char(official_name, "official_name")
        self._validator.validate_string(university_code, "university_code")
        self._validator.validate_only_char(location, "location")

        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IT"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Italia"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, location),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, official_name),
            x509.NameAttribute(NameOID.COMMON_NAME, university_code),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self.root_cert.subject)
            .public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now())
            .not_valid_after(datetime.datetime.now() + datetime.timedelta(days=365))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(public_key), critical=False)
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(self._public_key),
                critical=False
            )
            .sign(self._private_key, hashes.SHA256())
        )

        self._certificati_uni.append({
            "id_university": university_id,
            "certificate": cert,
            "revoked": None
        })

        return cert, self.root_cert

    def revoke_certificate(self, university_id: str) -> bool:
        self._validator.validate_string(university_id, "university_id")
        for entry in self._certificati_uni:
            if entry["id_university"] == university_id and entry["revoked"] is None:
                entry["revoked"] = datetime.date.today().isoformat()
                print(f"\n\t[MobilityCA] Certificato revocato per {university_id}")
                return True
        print(f"\n\t[MobilityCA] Nessun certificato attivo per {university_id}")
        return False

    def is_certificate_revoked(self, certificate) -> bool:
        return any(entry["certificate"] == certificate and entry["revoked"] is not None for entry in self._certificati_uni)

    def is_revoked_by_university(self, university_id: str) -> bool:
        self._validator.validate_string(university_id, "university_id")
        return any(entry["id_university"] == university_id and entry["revoked"] is not None for entry in self._certificati_uni)

    def find_university_id(self, certificate) -> str:
        for entry in self._certificati_uni:
            if entry["certificate"] == certificate:
                return entry["id_university"]
        raise ValueError("Certificato non trovato per questa università.")

    def certificate_matches(self, certificate) -> bool:
        return any(entry["certificate"] == certificate for entry in self._certificati_uni)

    def get_public_registry(self) -> List[dict]:
        """
        Restituisce un registro pubblico delle università accreditate,
        con info parziali e chiavi pubbliche serializzate.
        """
        registry = []
        for entry in self._certificati_uni:
            cert = entry["certificate"]
            info = {
                "university_id": entry["id_university"],
                "revoked": entry["revoked"],
                "public_key": cert.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode()
            }
            registry.append(info)
        return registry

    def verify_signature(self, message: bytes, signature: bytes, certificate) -> bool:
        try:
            certificate.public_key().verify(
                signature,
                message,
                padding=padding.PKCS1v15(),
                algorithm=hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"[MobilityCA] Firma non valida: {e}")
            return False
