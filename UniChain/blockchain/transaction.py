import hashlib
import json

class Transaction:
    def __init__(self, credential_hash, credential_unique_id, student_wallet_address, revocation_status=False):
        self.transaction_type = "EMISSION"  # Tipo di transazione (EMISSIONE o REVOCA)
        self.credential_hash = credential_hash
        self.credential_unique_id = credential_unique_id
        self.student_wallet_address = student_wallet_address
        self.revocation_status = revocation_status
        self.transaction_hash = self.calculate_hash()

    def calculate_hash(self):
        # Calcola l'hash della transazione
        transaction_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(transaction_string.encode('utf-8')).hexdigest()

    def sign_transaction(self, private_key):
        # Firma digitale della transazione
        # La firma è generata utilizzando la chiave privata dell'università emittente (simulata)
        # Puoi usare librerie come pycryptodome o cryptography per firmare effettivamente la transazione
        # La firma viene rappresentata come una stringa hash per semplicità.
        self.signature = private_key  # Simuliamo la firma come la chiave privata
        return self.signature

    def __repr__(self):
        return f"Transaction({self.transaction_type}, {self.credential_hash}, {self.student_wallet_address}, {self.revocation_status})"
