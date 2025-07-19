import hashlib
from typing import List, Tuple


def sha256(data: bytes) -> str:
    """
    Calcola l'hash SHA-256 di un blocco di dati.
    """
    return hashlib.sha256(data).hexdigest()


class MerkleTree:
    """
    Implementazione di un Merkle Tree basato su hash SHA-256.
    Permette di:
    - costruire l'albero da coppie (label, valore)
    - ottenere la root dell'albero
    - generare una proof per un campo specifico
    - verificare l'inclusione con `verify_proof`
    """

    def __init__(self, leaves: List[Tuple[str, str]]):
        """
        :param leaves: lista di tuple (label, value) in chiaro
        """
        self.leaves = [(label, sha256(value.encode())) for label, value in leaves]
        self.tree = []
        self._build_tree()

    def _build_tree(self):
        """
        Costruisce il Merkle Tree dal basso verso l'alto.
        """
        level = [leaf_hash for _, leaf_hash in self.leaves]
        self.tree.append(level)

        while len(level) > 1:
            new_level = []
            for i in range(0, len(level), 2):
                left = level[i]
                right = level[i + 1] if i + 1 < len(level) else left
                combined = sha256((left + right).encode())
                new_level.append(combined)
            level = new_level
            self.tree.append(level)

    def get_root(self) -> str:
        """
        Restituisce la Merkle Root dell'albero.
        """
        return self.tree[-1][0] if self.tree else None

    def get_proof(self, label: str) -> List[Tuple[str, str]]:
        """
        Genera una Merkle proof per il nodo identificato da `label`.
        :param label: nome dell'attributo
        :return: lista di coppie (direzione, hash) dove direzione è 'left' o 'right'
        """
        index = next((i for i, (l, _) in enumerate(self.leaves) if l == label), None)
        if index is None:
            raise ValueError("Campo non trovato tra le foglie.")

        proof = []
        for level in self.tree[:-1]:  # tutte le righe tranne la root
            sibling_index = index ^ 1
            if sibling_index < len(level):
                direction = "left" if sibling_index < index else "right"
                proof.append((direction, level[sibling_index]))
            index //= 2
        return proof

    @staticmethod
    def verify_proof(leaf_value: str, proof: List[Tuple[str, str]], root: str) -> bool:
        """
        Verifica che il valore fornito sia incluso nella Merkle root, tramite la proof.
        :param leaf_value: valore originale dell'attributo (non hashato)
        :param proof: lista di (direzione, hash)
        :param root: Merkle root attesa
        :return: True se il valore è valido rispetto alla root
        """
        current_hash = sha256(leaf_value.encode())
        for direction, sibling_hash in proof:
            if direction == "left":
                current_hash = sha256((sibling_hash + current_hash).encode())
            else:
                current_hash = sha256((current_hash + sibling_hash).encode())
        return current_hash == root

    def __repr__(self):
        return f"MerkleTree(root={self.get_root()})"
