import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

class Transaction:
    """
    Rappresenta una transazione nella blockchain UniChain.

    Può essere di due tipi:
    - EMISSIONE: indica l’emissione di una credenziale accademica (CAD).
    - REVOCA: indica la revoca di una credenziale precedentemente emessa.

    Ogni transazione include:
    - l’hash della credenziale (credential_hash),
    - un identificativo univoco della credenziale (credential_unique_id),
    - l’indirizzo del wallet dello studente (hash della chiave pubblica),
    - lo stato di revoca (revocation_status),
    - un hash identificativo della transazione stessa (transaction_hash),
    - una firma digitale RSA (signature) calcolata sull’hash della transazione.

    La firma può essere verificata tramite la chiave pubblica dell’ente firmatario.
    """

    def __init__(self, credential_hash, credential_unique_id, student_wallet_address,
                 revocation_status=False, transaction_type="EMISSIONE"):
        """
        Inizializza una transazione per l’emissione o la revoca di una credenziale.

        :param credential_hash: hash del contenuto del CAD (SHA-256)
        :param credential_unique_id: ID univoco della credenziale
        :param student_wallet_address: indirizzo hashato del wallet dello studente
        :param revocation_status: True se è una revoca, False se è un’emissione
        :param transaction_type: "EMISSIONE" o "REVOCA"
        """
        self.transaction_type = transaction_type
        self.credential_hash = credential_hash
        self.credential_unique_id = credential_unique_id
        self.student_wallet_address = student_wallet_address
        self.revocation_status = revocation_status

        self.signature = None  # Firma RSA in esadecimale
        self.transaction_hash = None
        self.calculate_transaction_hash()

    def calculate_transaction_hash(self):
        """
        Calcola l'hash della transazione a partire dai suoi attributi.
        Esclude la firma. Usato anche per la firma digitale.
        """
        transaction_string = json.dumps(self.to_dict(include_signature=False), sort_keys=True)
        self.transaction_hash = hashlib.sha256(transaction_string.encode('utf-8')).hexdigest()

    def sign_transaction(self, private_key):
        """
        Firma realmente la transazione con una chiave privata RSA.

        :param private_key: oggetto RSAPrivateKey (già caricato)
        """
        payload = self.transaction_hash.encode("utf-8")
        self.signature = private_key.sign(
            payload,
            padding.PKCS1v15(),
            hashes.SHA256()
        ).hex()

    def verify_signature(self, public_key_pem) -> bool:
        """
        Verifica che la firma RSA sia valida rispetto all’hash della transazione.

        :param public_key_pem: chiave pubblica dell’università in formato PEM
        :return: True se valida, False altrimenti
        """
        if not self.signature or not self.transaction_hash:
            return False

        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
            public_key.verify(
                bytes.fromhex(self.signature),
                self.transaction_hash.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            print("Errore nella verifica firma:", e)
            return False

    def to_dict(self, include_signature=True):
        """
        Serializza la transazione in un dizionario JSON-compatibile.

        :param include_signature: True se vuoi includere la firma nella serializzazione
        :return: dizionario serializzabile
        """
        data = {
            "transaction_type": self.transaction_type,
            "credential_hash": self.credential_hash,
            "credential_unique_id": self.credential_unique_id,
            "student_wallet_address": self.student_wallet_address,
            "revocation_status": self.revocation_status,
            "transaction_hash": self.transaction_hash,
        }
        if include_signature:
            data["signature"] = self.signature
        return data

    def __repr__(self):
        """
        Rappresentazione leggibile della transazione.
        """
        return (f"Transaction({self.transaction_type}, "
                f"{self.credential_hash}, "
                f"{self.student_wallet_address}, "
                f"{self.revocation_status})")
