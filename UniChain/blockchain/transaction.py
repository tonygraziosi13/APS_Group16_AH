import hashlib
import json

class Transaction:
    def __init__(self, credential_hash, credential_unique_id, student_wallet_address,
                 revocation_status=False, transaction_type="EMISSION"):
        """
        Inizializza una transazione per l'emissione o la revoca di una credenziale accademica.

        :param credential_hash: hash crittografico del CAD (es. SHA-256 del JSON)
        :param credential_unique_id: identificativo univoco della credenziale
        :param student_wallet_address: hash della chiave pubblica dello studente (wallet pseudonimo)
        :param revocation_status: booleano (False per emissione, True per revoca)
        :param transaction_type: "EMISSION" o "REVOCA"
        """
        self.transaction_type = transaction_type
        self.credential_hash = credential_hash
        self.credential_unique_id = credential_unique_id
        self.student_wallet_address = student_wallet_address
        self.revocation_status = revocation_status

        self.signature = None  # Firma digitale della transazione (simulata)
        self.transaction_hash = None  # Hash univoco della transazione (SHA-256)
        self.calculate_transaction_hash()

    def calculate_transaction_hash(self):
        """
        Calcola l'hash della transazione basandosi sui dati principali (esclusa la firma).
        Viene usato come identificatore univoco e come base per la firma.
        """
        transaction_string = json.dumps(self.to_dict(), sort_keys=True)
        self.transaction_hash = hashlib.sha256(transaction_string.encode('utf-8')).hexdigest()

    def sign_transaction(self, private_key):
        """
        Simula la firma della transazione usando una chiave privata.
        In futuro può essere sostituita da una firma reale con algoritmo RSA o ECDSA.
        """
        if self.transaction_hash:
            self.signature = private_key + self.transaction_hash

    @staticmethod
    def verify_signature(public_key) -> bool:
        """
        Placeholder per futura verifica crittografica della firma con chiave pubblica.
        Attualmente non implementato.
        """
        # TODO: implementare con chiave pubblica reale
        return True

    def to_dict(self):
        """
        Serializza la transazione in un dizionario pronto per l'hashing o salvataggio.
        La firma non è inclusa nell'hash originale per integrità crittografica.
        """
        return {
            "transaction_type": self.transaction_type,
            "credential_hash": self.credential_hash,
            "credential_unique_id": self.credential_unique_id,
            "student_wallet_address": self.student_wallet_address,
            "revocation_status": self.revocation_status,
            "transaction_hash": self.transaction_hash,
        }

    def __repr__(self):
        """
        Rappresentazione testuale leggibile della transazione, utile per debug e log.
        """
        return (f"Transaction({self.transaction_type}, "
                f"{self.credential_hash}, "
                f"{self.student_wallet_address}, "
                f"{self.revocation_status})")
