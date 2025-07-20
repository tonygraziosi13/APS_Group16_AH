import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from UniChain.credentials.academic_credential import AcademicCredential
from UniChain.structures.merkle_tree import MerkleTree


class StudentWallet:
    """
    Rappresenta il wallet personale di uno studente (es. Alice).
    Gestisce la generazione di chiavi, la memorizzazione di credenziali e
    la produzione di Presentation Proof con divulgazione selettiva.
    Supporta anche il Mobility Trust System per autenticazione in sola lettura.
    """

    def __init__(self, student_name="Alice"):
        self.student_name = student_name

        # Genera una coppia di chiavi RSA (privata/pubblica)
        self._private_key = self._generate_private_key()
        self._public_key = self._private_key.public_key()

        # Dizionario delle credenziali memorizzate: key = credential_unique_id
        self._credentials = {}

        # Punti di affidabilità (facoltativi)
        self.trust_points = 0

    @staticmethod
    def _generate_private_key():
        """
        Genera una chiave privata RSA a 2048 bit.
        """
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def get_wallet_address(self) -> str:
        """
        Restituisce l'indirizzo del wallet come hash SHA-256 della chiave pubblica serializzata.
        """
        pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return hashlib.sha256(pem).hexdigest()

    def store_credential(self, credential_id: str, credential: AcademicCredential):
        """
        Memorizza una credenziale nel wallet, indicizzata per ID.
        """
        self._credentials[credential_id] = credential
        print(f"[Wallet] Credenziale {credential_id} memorizzata con successo.")

    def get_credential(self, credential_id: str) -> AcademicCredential:
        """
        Recupera una credenziale tramite il suo ID.
        """
        return self._credentials.get(credential_id)

    def sign_data(self, data: bytes) -> bytes:
        """
        Firma un messaggio generico con la chiave privata dello studente.
        Tipico uso: firma di Merkle Root o Presentation Proof.
        """
        return self._private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

    def get_public_key_pem(self) -> str:
        """
        Restituisce la chiave pubblica dello studente in formato PEM.
        Necessaria per la verifica da parte di terzi.
        """
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

    def __repr__(self):
        """
        Rappresentazione semplificata del wallet (nome e primi caratteri dell'indirizzo).
        """
        return f"StudentWallet({self.student_name}, address={self.get_wallet_address()[:10]}...)"

    def generate_presentation_proof(self, credential_id: str, reveal_fields: list[str]) -> dict:
        """
        Genera una Presentation Proof con divulgazione selettiva degli attributi specificati.
        L'integrità dei dati viene garantita tramite Merkle Root e Merkle Proof.

        :param credential_id: ID della credenziale da presentare
        :param reveal_fields: lista dei nomi finali degli attributi da rivelare (es. ["name", "grade"])
        :return: dizionario JSON-serializzabile contenente la proof
        """

        # 1. Recupera la credenziale dal wallet
        credential = self.get_credential(credential_id)
        if not credential:
            raise ValueError("Credenziale non trovata nel wallet.")

        # 2. Serializza la credenziale in un dizionario
        full_data = credential.to_dict()

        # 3. Appiattisce il dizionario annidato in una lista (label, value)
        flat_attributes = []

        def flatten(prefix, value):
            if isinstance(value, dict):
                for k, v in value.items():
                    flatten(f"{prefix}.{k}", v)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    flatten(f"{prefix}[{i}]", item)
            else:
                flat_attributes.append((prefix, str(value)))

        flatten("credential", full_data)

        # 4. Costruisce il Merkle Tree con gli attributi
        merkle = MerkleTree(flat_attributes)
        merkle_root = merkle.get_root()

        # 5. Seleziona gli attributi da rivelare e costruisce le relative proof
        revealed = {}
        merkle_proofs = {}

        for label, value in flat_attributes:
            if any(label.endswith(field) for field in reveal_fields):
                revealed[label] = value
                merkle_proofs[label] = merkle.get_proof(label)

        # 6. Firma la Merkle Root con la chiave privata
        signature = self.sign_data(merkle_root.encode("utf-8"))

        # 7. Restituisce la Presentation Proof
        return {
            "credentialId": credential_id,
            "walletAddress": self.get_wallet_address(),
            "revealedAttributes": revealed,
            "merkleProofs": merkle_proofs,
            "merkleRoot": merkle_root,
            "signature": signature.hex(),
            "publicKey": self.get_public_key_pem()
        }
