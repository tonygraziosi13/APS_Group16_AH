from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from UniChain.structures.merkle_tree import MerkleTree


class Verifier:
    """
    Verifica una credenziale accademica confrontando dati e firma con quelli registrati on-chain.
    Include verifica firma, Merkle proof, integrità e stato di revoca.
    """

    def __init__(self, blockchain):
        self.blockchain = blockchain  # Istanza di Blockchain

    @staticmethod
    def verify_student_signature(merkle_root: str, signature_hex: str, public_key_pem: str) -> bool:
        """
        Verifica che la firma dello studente sulla Merkle Root sia valida.
        :param merkle_root: stringa della root
        :param signature_hex: firma digitale in esadecimale
        :param public_key_pem: chiave pubblica dello studente in PEM
        """
        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode())
            signature = bytes.fromhex(signature_hex)
            public_key.verify(
                signature,
                merkle_root.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print("[Verifier] Firma studente non valida:", e)
            return False

    @staticmethod
    def verify_merkle_proof(revealed_value: str, proof: list, merkle_root: str) -> bool:
        """
        Verifica la Merkle Proof per un attributo rivelato.
        """
        return MerkleTree.verify_proof(revealed_value, proof, merkle_root)

    def check_merkle_root_on_chain(self, credential_id: str, claimed_merkle_root: str) -> bool:
        """
        Verifica che la Merkle Root fornita corrisponda a quella salvata on-chain per EMISSION.
        """
        for block in self.blockchain.chain:
            tx = block.transaction
            if tx.credential_unique_id == credential_id and block.transaction_type == "EMISSION":
                return block.attributes_merkle_root == claimed_merkle_root
        return False

    def check_revocation_status(self, credential_id: str) -> bool:
        """
        Controlla se la credenziale è stata revocata.
        Ritorna True se la credenziale è ancora valida (NON revocata).
        """
        for block in reversed(self.blockchain.chain):  # Legge dal più recente
            tx = block.transaction
            if tx.credential_unique_id == credential_id:
                return not tx.revocation_status
        return False  # Non trovata → trattare come non valida
