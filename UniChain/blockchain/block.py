import hashlib
import json
from datetime import datetime, UTC


class Block:
    def __init__(self,
                 previous_hash,
                 transaction,
                 version,
                 block_number,
                 block_proposer,
                 signature,
                 hash_algorithm="SHA-256",
                 attributes_merkle_root=None,
                 validator_info="Validator Info"):
        """
        Rappresenta un blocco della blockchain UniChain.
        """
        self.version = version
        self.previous_hash = previous_hash
        self.timestamp = datetime.now(UTC).isoformat()

        self.transaction = transaction
        if not hasattr(transaction, "transaction_type"):
            raise ValueError("La transazione non ha un campo 'transaction_type' valido.")
        self.transaction_type = transaction.transaction_type

        self.tx_root = self.calculate_tx_root()
        self.hash_algorithm = hash_algorithm
        self.block_number = block_number
        self.validator_info = validator_info
        self.block_proposer = block_proposer
        self.attributes_merkle_root = attributes_merkle_root
        self.signature = signature

    def calculate_tx_root(self):
        """
        Calcola l'hash della transazione contenuta nel blocco.
        """
        return hashlib.sha256(self.transaction.transaction_hash.encode('utf-8')).hexdigest()

    def calculate_hash(self):
        """
        Calcola l'hash del blocco intero a partire dai suoi attributi serializzati.
        """
        block_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

    @property
    def block_hash(self):
        return self.calculate_hash()

    def to_dict(self):
        """
        Serializza il blocco per export o hashing.
        """
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

    def get_payload_to_sign(self):
        """
        Restituisce il payload (in bytes) da firmare per generare la firma del blocco.
        La firma non deve includere se stessa.
        """
        payload = {
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
            "attributes_merkle_root": self.attributes_merkle_root
        }
        payload_string = json.dumps(payload, sort_keys=True)
        return payload_string.encode("utf-8")

    def __repr__(self):
        return f"Block({self.version}, {self.transaction}, {self.block_number}, {self.block_hash})"
