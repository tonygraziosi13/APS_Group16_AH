from cryptography.hazmat.primitives.asymmetric import rsa
from UniChain.moblityCA.certificate_manager import CertificateManager
from UniChain.utils.validator import Validator


class MobilityCA:
    """
    MobilityCA rappresenta l’autorità centrale di accreditamento nel sistema UniChain.

    Responsabilità principali:
    - Generare e custodire la chiave privata della Root CA
    - Accreditare università rilasciando certificati X.509 firmati
    - Gestire la revoca dei certificati universitari
    - Verificare firme digitali tramite certificati
    - Gestire la graduatoria Mobility Trust Ranking (MTR)
    - Esporre un registro pubblico delle università accreditate
    """

    def __init__(self):
        # Generazione della coppia di chiavi della Root CA MobilityCA
        self._private_key = self._generate_private_key()
        self._public_key = self._private_key.public_key()

        self._validator = Validator()

        # Inizializzazione del gestore certificati interno
        self._certificate_manager = CertificateManager(
            private_key=self._private_key,
            public_key=self._public_key
        )
        self._university_objects = {}  # Mappa university_id → oggetto University

    def get_validator(self):
        return self._validator

    def get_university_objects(self):
        return self._university_objects

    @staticmethod
    def _generate_private_key():
        """
        Genera una chiave privata RSA (2048 bit) per la Root CA.
        """
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # --- API per le Università ---

    def issue_certificate(self, public_key, university_id, official_name, university_code, location, university_obj=None):
        """
        Rilascia un certificato digitale a una università accreditata.
        Verifica la correttezza dei parametri prima di invocare il CertificateManager.
        """
        self._validator.validate_string(university_id, "university_id")
        self._validator.validate_only_char(official_name, "official_name")
        self._validator.validate_string(university_code, "university_code")
        self._validator.validate_only_char(location, "location")

        if university_obj:
            self._university_objects[university_id] = university_obj

        return self._certificate_manager.issue_certificate(
            public_key=public_key,
            university_id=university_id,
            official_name=official_name,
            university_code=university_code,
            location=location
        )

    def revoke_certificate(self, university_id):
        """
        Revoca un certificato già rilasciato a un’università.
        """
        self._validator.validate_string(university_id, "university_id")
        return self._certificate_manager.revoke_certificate(university_id)

    def receive_revocation_request(self, message: bytes, signature: bytes, university_id: str) -> bool:
        """
        Riceve una richiesta firmata di revoca da parte di un’università.
        Se la firma è valida rispetto al certificato in archivio, la revoca viene eseguita.

        :param message: messaggio originale firmato (es. "Request to revoke")
        :param signature: firma digitale generata dalla chiave privata dell’università
        :param university_id: identificativo dell’università richiedente
        :return: True se revoca eseguita, False in caso di errore o firma non valida
        """
        self._validator.validate_string(university_id, "university_id")

        # Cerca il certificato associato all'università
        for entry in self._certificate_manager._certificati_uni:
            if entry["id_university"] == university_id:
                certificate = entry["certificate"]
                break
        else:
            print(f"[MobilityCA] Nessun certificato trovato per {university_id}")
            return False

        # Verifica la firma prima della revoca
        if self._certificate_manager.verify_signature(message, signature, certificate):
            print(f"[MobilityCA] Firma valida. Procedo con la revoca del certificato per {university_id}.")
            return self._certificate_manager.revoke_certificate(university_id)
        else:
            print(f"[MobilityCA] Firma NON valida. Revoca rifiutata per {university_id}.")
            return False

    def is_certificate_revoked(self, certificate):
        """
        Controlla se un certificato è stato revocato.
        """
        return self._certificate_manager.is_certificate_revoked(certificate)

    def get_root_certificate(self):
        """
        Restituisce il certificato della Root CA MobilityCA.
        """
        return self._certificate_manager.get_root_cert()

    def get_public_registry(self):
        """
        Restituisce il registro pubblico delle università accreditate.
        """
        return self._certificate_manager.get_public_registry()

    def verify_signature(self, message: bytes, signature: bytes, certificate) -> bool:
        """
        Verifica una firma digitale utilizzando il certificato fornito.
        """
        return self._certificate_manager.verify_signature(message, signature, certificate)

    # --- Mobility Trust Ranking (MTR) ---

    def get_mobility_trust_ranking(self, universities):
        """
        Restituisce la graduatoria ufficiale delle università
        ordinata in base ai Mobility Trust Points (MTP).
        """
        ranking = sorted(universities, key=lambda u: u.mobility_trust_points, reverse=True)

        print("\n====== MOBILITY TRUST RANKING ======")
        for i, uni in enumerate(ranking, start=1):
            print(f"{i}. {uni.official_name} - {uni.mobility_trust_points} MTP")
        print("====================================\n")

        return ranking
