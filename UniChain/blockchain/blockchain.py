from UniChain.blockchain.transaction import Transaction
from UniChain.blockchain.block import Block


class Blockchain:
    """
    Rappresenta la blockchain UniChain, responsabile della gestione
    delle transazioni di emissione e revoca dei CAD accademici.
    Ogni blocco è firmato digitalmente dall’università proponente.
    """
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Crea il blocco di genesi con una transazione fittizia.
        Non è firmato realmente.
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
        return self.chain[-1]

    def add_transaction(self, transaction):
        """
        Aggiunge una transazione alla lista pendente (non usata attualmente).
        """
        self.pending_transactions.append(transaction)

    def add_block(self, transaction, version, block_number, block_proposer_obj, attributes_merkle_root=None):
        """
        Crea e firma realmente un nuovo blocco, poi lo aggiunge alla catena.
        Il firmatario è l’università `block_proposer_obj` (oggetto University).
        """
        previous_block = self.get_latest_block()
        previous_hash = previous_block.block_hash

        # 1. Costruisci blocco senza firma
        temp_block = Block(
            previous_hash=previous_hash,
            transaction=transaction,
            version=version,
            block_number=block_number,
            block_proposer=block_proposer_obj.university_id,
            signature=None,
            attributes_merkle_root=attributes_merkle_root
        )

        # 2. Firma reale del blocco
        payload = temp_block.get_payload_to_sign()
        signature = block_proposer_obj.sign_message(payload).hex()

        # 3. Inserisci la firma nel blocco
        temp_block.signature = signature

        # 4. Aggiungi il blocco alla catena
        self.chain.append(temp_block)

        # 5. (Facoltativo) Logging
        print(f"Blocco #{block_number} aggiunto alla blockchain.")
        print(f"   - Proposto da: {block_proposer_obj.university_id}")
        print(f"   - Firma SHA256-RSA: {signature[:64]}...\n")

    def is_chain_valid(self):
        """
        Verifica la coerenza della catena:
        - Collegamento corretto tra blocchi
        - Hash coerente
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
                          version, block_number, block_proposer_obj, attributes_merkle_root=None):
        """
        Genera una transazione di revoca e la ancora sulla blockchain
        come blocco firmato digitalmente dall’università.
        """
        # Controlla se la credenziale esiste già ed è di tipo EMISSIONE
        found = False
        for block in reversed(self.chain):
            tx = block.transaction
            if tx.credential_unique_id == credential_unique_id:
                if tx.transaction_type == "EMISSIONE":
                    found = True
                    break
                elif tx.transaction_type == "REVOCA":
                    raise Exception(f"La credenziale {credential_unique_id} è già stata revocata.")
        if not found:
            raise Exception(f"Impossibile revocare: credenziale {credential_unique_id} non trovata nella blockchain.")

        # Se passa il controllo, crea la transazione di revoca
        revocation_tx = Transaction(
            credential_hash=credential_hash,
            credential_unique_id=credential_unique_id,
            student_wallet_address=student_wallet_address,
            revocation_status=True,
            transaction_type="REVOCA"
        )
        revocation_tx.sign_transaction(block_proposer_obj.private_key)

        # Aggiungi il blocco di revoca alla catena
        self.add_block(
            transaction=revocation_tx,
            version=version,
            block_number=block_number,
            block_proposer_obj=block_proposer_obj,
            attributes_merkle_root=attributes_merkle_root
        )


def is_credential_valid(self, credential_unique_id):
    """
    Controlla se la credenziale con l’ID dato è valida (non revocata).
    Restituisce True se non è stata revocata, False se esiste una revoca.
    """
    # Scorri la catena all’indietro per trovare la transazione più recente per quell’ID
    for block in reversed(self.chain):
        tx = block.transaction
        if tx.credential_unique_id == credential_unique_id:
            if tx.transaction_type == "REVOCA" and tx.revocation_status:
                return False  # È stata revocata
            elif tx.transaction_type == "EMISSIONE":
                return True  # Trovata emissione senza revoca successiva
    # Se non trovi nessuna transazione per quell’ID
    return False
