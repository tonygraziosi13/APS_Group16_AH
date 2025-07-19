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

        :param previous_hash: hash del blocco precedente
        :param transaction: oggetto Transaction (EMISSION/REVOCA)
        :param version: versione del protocollo blockchain
        :param block_number: posizione nella catena
        :param block_proposer: nodo che propone il blocco (es. Université de Rennes)
        :param signature: firma del nodo proponente
        :param hash_algorithm: algoritmo usato per tx_root e MerkleRoot
        :param attributes_merkle_root: Merkle Root degli attributi del CAD
        :param validator_info: informazioni opzionali sui nodi che hanno partecipato al consenso
        """
        self.version = version
        self.previous_hash = previous_hash
        self.timestamp = datetime.now(UTC).isoformat()  # ISO 8601 + timezone UTC

        self.transaction = transaction

        # Protezione in caso la transazione non abbia il campo richiesto
        if not hasattr(transaction, "transaction_type"):
            raise ValueError("La transazione non ha un campo 'transaction_type' valido.")
        self.transaction_type = transaction.transaction_type

        self.tx_root = self.calculate_tx_root()  # Hash della transazione
        self.hash_algorithm = hash_algorithm
        self.block_number = block_number
        self.validator_info = validator_info
        self.block_proposer = block_proposer
        self.attributes_merkle_root = attributes_merkle_root
        self.signature = signature

    def calculate_tx_root(self):
        """
        Calcola l'hash della transazione contenuta nel blocco.
        Questo valore è utilizzato come `tx_root`.
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
        """
        Proprietà dinamica che calcola l'hash del blocco corrente.
        """
        return self.calculate_hash()

    def to_dict(self):
        """
        Converte l'oggetto Block in un dizionario serializzabile.
        Utile per calcolo dell'hash, logging o export JSON.
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

    def __repr__(self):
        return f"Block({self.version}, {self.transaction}, {self.block_number}, {self.block_hash})"
