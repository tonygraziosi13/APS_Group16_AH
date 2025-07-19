import hashlib
from UniChain.blockchain.transaction import Transaction
from UniChain.blockchain.blockchain import Blockchain

def verify_signature(transaction, public_key):
    try:
        # Verifica che la firma sia corretta
        if transaction.signature == public_key + transaction.transaction_hash:
            print(f"Firma della transazione {transaction.transaction_hash} verificata correttamente.")
            return True
        else:
            return False
    except Exception as e:
        print(f"Errore nella verifica della firma: {e}")
        return False

def main():
    # Crea la credenziale per uno studente
    credential_hash = hashlib.sha256("Credential for Alice".encode('utf-8')).hexdigest()
    credential_unique_id = "uni_credential_001"
    student_wallet_address = hashlib.sha256("student_wallet_12345".encode('utf-8')).hexdigest()

    # Crea la transazione
    transaction = Transaction(credential_hash, credential_unique_id, student_wallet_address)

    # Firma la transazione con una chiave privata simulata
    university_private_key = "private_key_123"
    transaction.sign_transaction(university_private_key)

    # Verifica la firma con una chiave pubblica simulata
    university_public_key = "private_key_123"  # In un vero scenario sarebbe una chiave pubblica separata
    if verify_signature(transaction, university_public_key):
        print("Firma della transazione verificata.\n")
    else:
        print("Firma della transazione non valida.\n")

    # Crea la blockchain e aggiungi la transazione
    blockchain = Blockchain()
    blockchain.add_transaction(transaction)
    blockchain.add_block(transaction, version="1.0", block_number=1, block_proposer="Université de Rennes", signature=transaction.signature)

    # Verifica la validità della blockchain
    print("La blockchain è valida?", blockchain.is_chain_valid())

    print("\n--- Fine simulazione ---\n")

if __name__ == "__main__":
    main()
