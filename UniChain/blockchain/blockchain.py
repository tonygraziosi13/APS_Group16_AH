from blockchain.transaction import Transaction
from blockchain.block import Block

class Blockchain:
    def __init__(self):
        self.chain = []  # Lista che contiene i blocchi
        self.pending_transactions = []  # Transazioni pendenti che devono essere incluse nel prossimo blocco
        self.create_genesis_block()

    def create_genesis_block(self):
        # Crea il blocco iniziale (genesi)
        genesis_transaction = Transaction(credential_hash="0", credential_unique_id="0", student_wallet_address="0")
        genesis_block = Block(previous_hash="1", transaction=genesis_transaction, version="1.0", block_number=0, block_proposer="genesis_node", signature="genesis_signature")
        self.chain.append(genesis_block)

    def add_block(self, transaction, version, block_number, block_proposer, signature):
        # Aggiungi una transazione alla blockchain
        last_block = self.chain[-1] if self.chain else None
        new_block = Block(
            previous_hash=last_block.block_hash if last_block else "0",
            transaction=transaction,
            version=version,
            block_number=block_number,
            block_proposer=block_proposer,
            signature=signature
        )
        self.chain.append(new_block)

    def get_last_block(self):
        return self.chain[-1] if self.chain else None

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def __repr__(self):
        return f"Blockchain(chain={self.chain})"
