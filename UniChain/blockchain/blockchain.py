from UniChain.blockchain.transaction import Transaction
from UniChain.blockchain.block import Block


class Blockchain:
    """
    Rappresenta la blockchain UniChain, responsabile della gestione
    delle transazioni di emissione e revoca dei CAD accademici.
    Ogni blocco è firmato digitalmente dall’università proponente.
    """
    def __init__(self, mobility_ca):
        self.chain = []
        self.pending_transactions = []
        self.mobility_ca = mobility_ca
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
        Esegue il consenso PBFT per finalizzare e aggiungere un blocco alla blockchain.
        """
        # Controlla se l'università proponente è accreditata
        certificate = block_proposer_obj.get_certificate()
        if self.mobility_ca.is_certificate_revoked(certificate):
            raise Exception(
                f"[Blockchain] Errore: l'università {block_proposer_obj.official_name} non è più accreditata.")

        previous_block = self.get_latest_block()
        previous_hash = previous_block.block_hash

        # === [Fase 1] Pre-prepare: il Primary (block_proposer) costruisce il blocco ===
        temp_block = Block(
            previous_hash=previous_hash,
            transaction=transaction,
            version=version,
            block_number=block_number,
            block_proposer=block_proposer_obj.university_id,
            signature=None,
            attributes_merkle_root=attributes_merkle_root
        )

        payload = temp_block.get_payload_to_sign()
        signature = block_proposer_obj.sign_message(payload).hex()
        temp_block.signature = signature

        # === [Fase 2] Prepare: invia a tutti i Replicas per la validazione ===
        all_unis = [u for u in self.mobility_ca.get_public_registry() if not u["revoked"]]
        replicas = [u for u in all_unis if u["university_id"] != block_proposer_obj.university_id]
        R = (len(all_unis) - 1) // 3
        quorum = 2 * R + 1

        prepare_votes = 0
        for r_dict in replicas:
            try:
                # Simulazione: assumiamo che ogni replica accetti
                prepare_votes += 1
                print(f"[PBFT] {r_dict['official_name']} → PREPARE OK.")
            except Exception as e:
                print(f"[PBFT] {r_dict['official_name']} → PREPARE FAIL: {e}")

        if prepare_votes >= quorum:
            print(f"[PBFT] Quorum raggiunto ({prepare_votes}/{len(replicas)}). Commit finale del blocco.")
            self.chain.append(temp_block)

            block_proposer_obj.add_trust_point(1, reason="blocco proposto e validato")

            for r_dict in replicas:
                uni_obj = block_proposer_obj.get_peer_by_id(r_dict["university_id"])  # Da implementare
                if uni_obj:
                    uni_obj.add_trust_point(0.5, reason="partecipazione al consenso")

            print(f"[Blockchain] Blocco #{block_number} aggiunto alla blockchain.")
            print(f"   - Proposto da: {block_proposer_obj.official_name}")
            print(f"   - Firma SHA256-RSA: {signature[:64]}...\n")
        else:
            print(f"[PBFT] Quorum NON raggiunto ({prepare_votes}/{len(replicas)}). Blocco SCARTATO.")
            raise Exception("[PBFT] Consenso fallito. Il blocco non è stato aggiunto.")

    def get_all_universities(self):
        """
        Raccoglie tutte le università che hanno proposto almeno un blocco (escluse quelle revocate).
        """
        proposers = {block.block_proposer for block in self.chain if block.block_proposer != "Genesis Block"}
        return [u for uid, u in self.mobility_ca.get_university_objects().items() if uid in proposers]

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
