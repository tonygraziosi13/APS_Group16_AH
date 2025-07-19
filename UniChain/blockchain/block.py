import hashlib
import json
import time

class Block:
    def __init__(self, previous_hash, transaction, version, block_number, block_proposer, signature, hash_algorithm="SHA-256", attributes_merkle_root=None):
        self.version = version
        self.previous_hash = previous_hash
        self.timestamp = str(time.time())  # Timestamp del blocco
        self.transaction = transaction
        self.transaction_type = transaction.transaction_type
        self.tx_root = self.calculate_tx_root()  # Radice Merkle della transazione
        self.hash_algorithm = hash_algorithm
        self.block_number = block_number
        self.validator_info = "Validator Info"  # Dati del validatore (facoltativo)
        self.block_proposer = block_proposer  # Proponente del blocco
        self.attributes_merkle_root = attributes_merkle_root
        self.signature = signature
        # Non impostiamo direttamente `block_hash` nel costruttore
        # self.block_hash = None  # Rimosso, perché non possiamo assegnare una proprietà

    def calculate_tx_root(self):
        # Calcola la radice Merkle della transazione
        return hashlib.sha256(self.transaction.transaction_hash.encode('utf-8')).hexdigest()

    def calculate_hash(self):
        # Calcola l'hash del blocco
        block_string = json.dumps(self.to_dict(), sort_keys=True)  # Usa to_dict per serializzare
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

    @property
    def block_hash(self):
        # Calcola l'hash quando viene richiesto, senza interferire con la proprietà
        return self.calculate_hash()

    def to_dict(self):
        # Converte l'oggetto Block in un dizionario per serializzazione
        return {
            "version": self.version,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "transaction": self.transaction.to_dict(),
            "transaction_type": self.transaction_type,
            "tx_root": self.tx_root,
            "hash_algorithm": self.hash_algorithm,
            "block_number": self.block_number,
            "validator_info": self.validator_info,
            "block_proposer": self.block_proposer,
            "attributes_merkle_root": self.attributes_merkle_root,
            "signature": self.signature,
        }

    def __repr__(self):
        return f"Block({self.version}, {self.transaction}, {self.block_number}, {self.block_hash})"
