from UniChain.blockchain.blockchain import Blockchain
from UniChain.blockchain.transaction import Transaction

def main():
    # 1. Crea la blockchain
    blockchain = Blockchain()

    # 2. Crea una transazione di emissione (es. Alice)
    emission_tx = Transaction(
        credential_hash="abc123hash",
        credential_unique_id="cred001",
        student_wallet_address="wallet_xyz"
    )
    emission_tx.sign_transaction("UNIVERSITY_PRIVATE_KEY")

    # 3. Aggiungi il blocco di emissione
    blockchain.add_block(
        transaction=emission_tx,
        version="1.0",
        block_number=1,
        block_proposer="Université de Rennes",
        signature="signed_by_rennes"
    )

    # 4. Revoca la credenziale
    blockchain.revoke_credential(
        credential_unique_id="cred001",
        credential_hash="abc123hash",
        student_wallet_address="wallet_xyz",
        version="1.0",
        block_number=2,
        block_proposer="Université de Rennes",
        signature="signed_by_rennes"
    )

    # 5. Stampa la blockchain
    print("\n📦 Stato attuale della blockchain:\n")
    for block in blockchain.chain:
        print(f"Blocco #{block.block_number}")
        print(f"Tipo transazione: {block.transaction_type}")
        print(f"Hash blocco: {block.block_hash}")
        print(f"Transazione: {block.transaction}")
        print(f"Revocata: {block.transaction.revocation_status}")
        print("-" * 60)

# 🔥 IMPORTANTE: chiama la funzione main!
if __name__ == "__main__":
    main()
