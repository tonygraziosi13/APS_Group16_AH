from UniChain.blockchain.transaction import Transaction
from UniChain.blockchain.block import Block


class Blockchain:
    def __init__(self):
        """
        Inizializza la blockchain con un blocco di genesi.
        """
        self.chain = []
        self.pending_transactions = []  # Non usato attualmente, ma pronto per future estensioni
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Crea il blocco di genesi con una transazione fittizia.
        Questo blocco serve come punto di partenza della blockchain.
        """
        fake_transaction = Transaction(
            credential_hash="fake_hash_credential",
            credential_unique_id="fake_unique_id",
            student_wallet_address="fake_wallet_address"
        )

        genesis_block = Block(
            previous_hash="0",
            transaction=fake_transaction,
            version="1.0",
            block_number=0,
            block_proposer="Genesis Block",
            signature="Genesis Signature"
        )

        self.chain.append(genesis_block)

    def get_latest_block(self):
        """
        Restituisce l'ultimo blocco nella catena.
        """
        return self.chain[-1]

    def add_transaction(self, transaction):
        """
        (Facoltativo) Aggiunge una transazione alla lista pendente.
        Non utilizzato nella logica corrente, ma utile in futuri modelli a più transazioni.
        """
        self.pending_transactions.append(transaction)

    def add_block(self, transaction, version, block_number, block_proposer, signature):
        """
        Aggiunge un nuovo blocco alla blockchain con i dati specificati.
        Calcola l'hash del blocco precedente e costruisce un nuovo blocco da appendere alla catena.
        """
        previous_block = self.get_latest_block()
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

    def is_chain_valid(self):
        """
        Verifica l'integrità della blockchain:
        - ogni blocco deve puntare correttamente al blocco precedente
        - l'hash di ogni blocco deve essere corretto
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.previous_hash != previous_block.block_hash:
                return False
            if current_block.block_hash != current_block.calculate_hash():
                return False

        return True

    def revoke_credential(self, credential_unique_id, credential_hash, student_wallet_address,
                          version, block_number, block_proposer, signature):
        """
        Genera una transazione di revoca (REVOCA) per una credenziale accademica
        e la ancora sulla blockchain sotto forma di nuovo blocco.
        """
        revocation_tx = Transaction(
            credential_hash=credential_hash,
            credential_unique_id=credential_unique_id,
            student_wallet_address=student_wallet_address,
            revocation_status=True,
            transaction_type="REVOCA"
        )
        revocation_tx.sign_transaction("UNIVERSITY_PRIVATE_KEY")

        self.add_block(
            transaction=revocation_tx,
            version=version,
            block_number=block_number,
            block_proposer=block_proposer,
            signature=signature
        )
