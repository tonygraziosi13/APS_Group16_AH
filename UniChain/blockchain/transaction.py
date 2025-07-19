import hashlib
import json

class Transaction:
    def __init__(self, credential_hash, credential_unique_id, student_wallet_address, revocation_status=False):
        # Definizione dei parametri base della transazione
        self.transaction_type = "EMISSION"  # Tipo di transazione (EMISSION o REVOCA)
        self.credential_hash = credential_hash  # Hash della credenziale
        self.credential_unique_id = credential_unique_id  # ID univoco della credenziale
        self.student_wallet_address = student_wallet_address  # Indirizzo del wallet dello studente
        self.revocation_status = revocation_status  # Stato della credenziale
        self.signature = None  # La firma sarà aggiunta successivamente
        self.transaction_hash = None  # Hash da calcolare dopo l'inizializzazione

        self.calculate_transaction_hash()  # Calcoliamo l'hash subito dopo la creazione

    def calculate_transaction_hash(self):
        # Calcola l'hash della transazione (se non è stato ancora calcolato)
        transaction_string = json.dumps(self.to_dict(), sort_keys=True)
        self.transaction_hash = hashlib.sha256(transaction_string.encode('utf-8')).hexdigest()

    def sign_transaction(self, private_key):
        # Simula la firma della transazione con una chiave privata "simulata"
        if self.transaction_hash:  # Assicuriamoci che l'hash sia stato calcolato prima della firma
            self.signature = private_key + self.transaction_hash  # Combina la chiave privata con l'hash

    def to_dict(self):
        # Restituisce i dati della transazione senza calcolare l'hash
        return {
            "transaction_type": self.transaction_type,
            "credential_hash": self.credential_hash,
            "credential_unique_id": self.credential_unique_id,
            "student_wallet_address": self.student_wallet_address,
            "revocation_status": self.revocation_status,
            "transaction_hash": self.transaction_hash,
        }

    def __repr__(self):
        return f"Transaction({self.transaction_type}, {self.credential_hash}, {self.student_wallet_address}, {self.revocation_status})"
