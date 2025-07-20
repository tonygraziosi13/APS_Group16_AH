import datetime
from typing import List
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from UniChain.utils.validator import Validator


class CertificateManager:
    """
    Gestisce l'autorità certificatrice MobilityCA.

    Funzionalità principali:
    - genera il certificato root (Root CA)
    - accredita le università (rilascia certificati firmati)
    - mantiene il registro pubblico dei certificati
    - supporta la revoca dei certificati
    - verifica firme tramite certificati X.509
    """

    def __init__(self, private_key, public_key):
        """
        Inizializza la MobilityCA con chiavi e un certificato root autofirmato.
        """
        self._private_key = private_key
        self._public_key = public_key
        self._certificati_uni: List[dict] = []  # Elenco certificati rilasciati
        self._generate_root_cert()
        self._validator = Validator()

    def _generate_root_cert(self):
        """
        Genera un certificato autofirmato che rappresenta la Root CA MobilityCA.
        """
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
            .not_valid_after(datetime.datetime.now() + datetime.timedelta(days=3650))  # 10 anni
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(self._private_key, hashes.SHA256())
        )

    def get_root_cert(self):
        """
        Restituisce il certificato Root CA.
        """
        return self.root_cert

    def issue_certificate(self, public_key, university_id, official_name, university_code, location):
        """
        Rilascia un certificato X.509 firmato da MobilityCA a un'università.

        :param public_key: chiave pubblica dell’università
        :param university_id: identificativo interno univoco
        :param official_name: nome ufficiale dell’università
        :param university_code: codice breve dell’università
        :param location: città/località
        :return: (certificato rilasciato, root_cert)
        """
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
            .not_valid_after(datetime.datetime.now() + datetime.timedelta(days=365))  # 1 anno
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
            "official_name": official_name,
            "certificate": cert,
            "revoked": None
        })

        return cert, self.root_cert

    def revoke_certificate(self, university_id: str) -> bool:
        """
        Revoca un certificato già rilasciato a un'università.

        :param university_id: identificatore dell’università
        :return: True se revocato, False se non trovato
        """
        self._validator.validate_string(university_id, "university_id")

        for entry in self._certificati_uni:
            if entry["id_university"] == university_id and entry["revoked"] is None:
                entry["revoked"] = datetime.date.today().isoformat()
                print(f"\n\t[MobilityCA] Certificato revocato per {university_id}")
                return True

        print(f"\n\t[MobilityCA] Nessun certificato attivo per {university_id}")
        return False

    def is_certificate_revoked(self, certificate) -> bool:
        """
        Verifica se un certificato è stato revocato.
        """
        return any(entry["certificate"] == certificate and entry["revoked"] is not None
                   for entry in self._certificati_uni)

    def is_revoked_by_university(self, university_id: str) -> bool:
        """
        Verifica se un'università ha un certificato revocato.

        :param university_id: ID interno dell’università
        :return: True se revocato, False altrimenti
        """
        self._validator.validate_string(university_id, "university_id")
        return any(entry["id_university"] == university_id and entry["revoked"] is not None
                   for entry in self._certificati_uni)

    def find_university_id(self, certificate) -> str:
        """
        Restituisce l'ID dell’università associato a un certificato.
        """
        for entry in self._certificati_uni:
            if entry["certificate"] == certificate:
                return entry["id_university"]
        raise ValueError("Certificato non trovato per questa università.")

    def certificate_matches(self, certificate) -> bool:
        """
        Verifica se un certificato esiste nel registro MobilityCA.
        """
        return any(entry["certificate"] == certificate for entry in self._certificati_uni)

    def get_public_registry(self) -> List[dict]:
        """
        Restituisce il registro pubblico delle università accreditate.
        Include: ID, stato revoca e chiave pubblica (PEM).
        """
        registry = []
        for entry in self._certificati_uni:
            cert = entry["certificate"]
            info = {
                "university_id": entry["id_university"],
                "official_name": entry["official_name"],
                "revoked": entry["revoked"],
                "public_key": cert.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode()
            }
            registry.append(info)
        return registry

    @staticmethod
    def verify_signature(message: bytes, signature: bytes, certificate) -> bool:
        """
        Verifica una firma digitale usando la chiave pubblica di un certificato X.509.

        :param message: messaggio originale firmato
        :param signature: firma digitale
        :param certificate: certificato usato per verificare la firma
        :return: True se valida, False altrimenti
        """
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
