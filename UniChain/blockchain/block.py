import hashlib
import json
import time

class Block:
    def __init__(self, previous_hash, transaction, version, block_number, block_proposer, signature):
        self.version = version
        self.previous_hash = previous_hash
        self.timestamp = str(time.time())  # Timestamp di quando il blocco è creato
        self.transaction = transaction
        self.block_number = block_number
        self.block_hash = self.calculate_hash()
        self.block_proposer = block_proposer  # Nodo che ha proposto il blocco
        self.signature = signature  # Firma del blocco

    def calculate_hash(self):
        # Calcola l'hash del blocco
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

    def __repr__(self):
        return f"Block({self.version}, {self.transaction}, {self.block_number}, {self.block_hash})"
