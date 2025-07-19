import hashlib
from UniChain.blockchain.transaction import Transaction
from UniChain.blockchain.block import Block


class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        # Crea una transazione fittizia per il blocco di genesi
        fake_transaction = Transaction(
            credential_hash="fake_hash_credential",
            credential_unique_id="fake_unique_id",
            student_wallet_address="fake_wallet_address"
        )

        # Crea il blocco genesi con una transazione fittizia
        genesis_block = Block(
            previous_hash="0",  # Nessun blocco precedente
            transaction=fake_transaction,  # La transazione fittizia
            version="1.0",  # Versione del blocco
            block_number=0,  # Numero del blocco
            block_proposer="Genesis Block",  # Proponente del blocco
            signature="Genesis Signature"  # Firma del blocco
        )

        # Aggiungi il blocco genesi alla blockchain
        self.chain.append(genesis_block)

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def add_block(self, transaction, version, block_number, block_proposer, signature):
        if len(self.pending_transactions) > 0:
            # Aggiungi un blocco con la transazione
            previous_block = self.chain[-1]
            previous_hash = previous_block.block_hash

            block = Block(
                previous_hash=previous_hash,
                transaction=transaction,
                version=version,
                block_number=block_number,
                block_proposer=block_proposer,
                signature=signature
            )
            self.chain.append(block)
            self.pending_transactions = []  # Resetta le transazioni pendenti

    def is_chain_valid(self):
        # Verifica la validità della blockchain
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.previous_hash != previous_block.block_hash:
                return False
            if current_block.block_hash != current_block.calculate_hash():
                return False
        return True
