import hashlib

from UniChain.moblityCA.mobilityCA import MobilityCA
from UniChain.university.university import University
from UniChain.wallet.student_wallet import StudentWallet
from UniChain.credentials.academic_credential import AcademicCredential
from UniChain.structures.credential_subject import CredentialSubject
from UniChain.structures.degree import Degree
from UniChain.structures.enrollment import Enrollment
from UniChain.structures.exam_record import ExamRecord
from UniChain.structures.issuer import Issuer
from UniChain.structures.validity_period import ValidityPeriod
from UniChain.structures.proof import Proof
from UniChain.blockchain.blockchain import Blockchain
from UniChain.blockchain.transaction import Transaction
from UniChain.university.verifier import Verifier
from UniChain.structures.merkle_tree import MerkleTree

from datetime import datetime

# === [FASE 1] ACCREDITAMENTO ===
print("[Fase 1] ACCREDITAMENTO DI 4 UNIVERSITA PRESSO UNICHAIN\n")

mobility_ca = MobilityCA()

u_rennes = University("urn:rennes", "Université de Rennes", "FR-REN001", "Francia", mobility_ca)
u_salerno = University("urn:unisa", "Università di Salerno", "IT-SAL001", "Italia", mobility_ca)
u_bologna = University("urn:unibo", "Università di Bologna", "IT-BO001", "Italia", mobility_ca)
u_lisboa = University("urn:ulisboa", "Universidade de Lisboa", "PT-LIS001", "Portogallo", mobility_ca)

for u in [u_rennes, u_salerno, u_bologna, u_lisboa]:
    u.request_accreditation()

# === [FASE 2] RICHIESTA CAD DA PARTE DI ALICE ===
print("\n[Fase 2] ALICE CHIEDE LA CREDENZIALE ALL'UNIVERSITE DE RENNES PER IL SUO PERIODO ERASMUS\n")

alice_wallet = StudentWallet("Alice")

credential_subject = CredentialSubject(
    student_id="alice001",
    name="Alice Rossi",
    date_of_birth="2002-07-11",
    residence="Salerno",
    phone_number="+393331234567",
    email="alice.rossi@example.com",
    validator = u_rennes.mobility_ca.get_validator()  # usa validator condiviso
)

enrollment = Enrollment(
    academic_year=2024,
    regulation_year=2023,
    enrollment_date="2023-10-01",
    faculty="Informatica",
    course_name="Informatica",
    course_code="INF2024",
    career_status="attivo"
)

degree = Degree(
    title_name="Semestre Erasmus",
    degree_level="certificazione",
    graduation_date="2025-04-15",
    final_grade="0",
    awarding_institution=u_rennes.official_name,
    thesis_title="",
    honors=""
)

exams = [
    ExamRecord("Algoritmi e Protocolli per la Sicurezza", "0622720", "scritto", "obbligatoria", 24, 6, "2025-01-15", "Informatica"),
    ExamRecord("Intelligenza Artificiale", "0622730", "orale", "obbligatoria", 27, 6, "2025-02-10", "Informatica"),
    ExamRecord("Reti di Calcolatori", "0622740", "scritto", "obbligatoria", 30, 6, "2025-03-01", "Informatica")
]

validity = ValidityPeriod(
    issued_at=datetime.now().isoformat()
)

issuer = Issuer(
    issuer_id=u_rennes.university_id,
    name=u_rennes.official_name,
    location=u_rennes.location
)

cred = AcademicCredential(
    subject=credential_subject,
    degree=degree,
    enrollement=enrollment,
    validity=validity,
    issuer=issuer,
    exams=exams,
    optional_activities=[]
)

# === [FASE 3] FIRMA UNIVERSITARIA E INVIO ===
print("\n[Fase 3] L'UNIVERSITE DE RENNES EMETTE IL CAD, LO FIRMA E LO INVIA AD ALICE\n")

# Firma il CAD
serialized = str(cred.to_dict()).encode("utf-8")
signature = u_rennes.sign_message(serialized)

proof = Proof(
    signature_value=signature.hex(),
    verification_method=u_rennes.get_serialized_public_key()
)

cred.set_proof(proof)

# Alice riceve la credenziale nel wallet
credential_id = "CAD-ALICE-ERASMUS-FR001"
alice_wallet.store_credential(credential_id, cred)

# === [FASE 4] ANCORAGGIO SULLA BLOCKCHAIN ===
blockchain = Blockchain()

# Calcolo hash CAD per la transazione
cred_hash = hashlib.sha256(str(cred.to_dict()).encode()).hexdigest()
wallet_address = alice_wallet.get_wallet_address()

tx = Transaction(
    credential_hash=cred_hash,
    credential_unique_id=credential_id,
    student_wallet_address=wallet_address
)
tx.sign_transaction("UNIVERSITY_PRIVATE_KEY")  # simulata

# Costruzione del Merkle Tree (anche se non usato direttamente nei blocchi, serve la root)
flat_attrs = []
def flatten(prefix, val):
    if isinstance(val, dict):
        for k, v in val.items():
            flatten(f"{prefix}.{k}", v)
    elif isinstance(val, list):
        for i, v in enumerate(val):
            flatten(f"{prefix}[{i}]", v)
    else:
        flat_attrs.append((prefix, str(val)))

flatten("credential", cred.to_dict())
merkle_root = MerkleTree(flat_attrs).get_root()

# Inserimento nella blockchain
blockchain.add_block(
    transaction=tx,
    version="1.0",
    block_number=1,
    block_proposer=u_rennes.university_id,
    signature="FIRMA_BLOCCO_SIMULATA",
)
blockchain.chain[-1].attributes_merkle_root = merkle_root

# === [FASE 5] PRESENTAZIONE SELETTIVA A UNISA ===
print("\n[Fase 4] ALICE PRESENTA SOLO PARTE DEL CAD ALL'UNIVERSITA DI SALERNO PER IL RICONOSCIMENTO DEI CREDITI\n")

reveal_fields = ["courseName", "courseCode", "grade"]
presentation_proof = alice_wallet.generate_presentation_proof(credential_id, reveal_fields)

verifier = Verifier(blockchain)

# Verifica firma
print("Verifica firma di Alice sulla Merkle Root...")
is_signature_valid = verifier.verify_student_signature(
    merkle_root=presentation_proof["merkleRoot"],
    signature_hex=presentation_proof["signature"],
    public_key_pem=presentation_proof["publicKey"]
)
print(f"Firma di Alice: {'VALIDA' if is_signature_valid else 'NON VALIDA'}\n")

# Verifica root
print("Verifica corrispondenza Merkle Root sulla blockchain...")
is_root_on_chain = verifier.check_merkle_root_on_chain(credential_id, presentation_proof["merkleRoot"])
print(f"Merkle Root ancorata: {'TROVATA' if is_root_on_chain else 'NON TROVATA'}\n")

# Stato revoca
print("Verifica stato di revoca della credenziale...")
is_not_revoked = verifier.check_revocation_status(credential_id)
print(f"Stato della credenziale: {'NON REVOCATA' if is_not_revoked else 'REVOCATA'}\n")

# Verifica singole Merkle Proof
for label, value in presentation_proof["revealedAttributes"].items():
    proof = presentation_proof["merkleProofs"][label]
    print(f"Verifica Merkle Proof per: {label} = {value}")
    is_valid = verifier.verify_merkle_proof(value, proof, presentation_proof["merkleRoot"])
    print(f"Proof: {'VALIDA' if is_valid else 'NON VALIDA'}\n")

# Esito finale
if is_signature_valid and is_root_on_chain and is_not_revoked:
    print("[RISULTATO FINALE] ALICE RISULTA AUTENTICATA E LA SUA CREDENZIALE RISULTA VALIDA.\n")
else:
    print("[RISULTATO FINALE] VERIFICA FALLITA.\n")
