import time
import hashlib
import sys
import json
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
from UniChain.structures.merkle_tree import MerkleTree
from UniChain.blockchain.transaction import Transaction
from UniChain.blockchain.blockchain import Blockchain


# ============ SETUP ============

print("\n=== TEST DI PERFORMANCE UniChain ===\n")

# Crea MobilityCA e università
mobility_ca = MobilityCA()
u_rennes = University("urn:rennes", "Université de Rennes", "FR-REN001", "Francia", mobility_ca)
u_salerno = University("urn:unisa", "Università di Salerno", "IT-SAL001", "Italia", mobility_ca)
u_bologna = University("urn:unibo", "Università di Bologna", "IT-BO001", "Italia", mobility_ca)
u_lisboa = University("urn:ulisboa", "Universidade de Lisboa", "PT-LIS001", "Portogallo", mobility_ca)

# Accredita università
for u in [u_rennes, u_salerno, u_bologna, u_lisboa]:
    u.request_accreditation()

# Imposta la rete di peer per il PBFT
all_universities = [u_rennes, u_salerno, u_bologna, u_lisboa]
for u in all_universities:
    u.set_peers([peer for peer in all_universities if peer != u])

# Crea wallet per Alice
alice_wallet = StudentWallet("Alice")

# Costruisci una credenziale
subject = CredentialSubject(
    student_id="8742",
    name="Alice Rossi",
    date_of_birth="2002-07-11",
    residence="Salerno",
    phone_number="+393331234567",
    email="alice.rossi@studenti.it",
    validator=u_rennes.mobility_ca.get_validator()
)

degree = Degree(
    title_name="Laurea in Ingegneria Informatica",
    degree_level="triennale",
    graduation_date="2024-09-15",
    final_grade="100",
    awarding_institution=u_rennes.official_name,
    thesis_title="UN SISTEMA PER LA GESTIONE DI NOTIFICHE WEB PUSH",
    honors=""
)

enrollment = Enrollment(
    academic_year=2024,
    regulation_year=2023,
    enrollment_date="2023-10-01",
    faculty="INGEGNERIA INFORMATICA",
    course_name="CORSO DI LAUREA MAGISTRALE",
    course_code="LM-32",
    career_status="attivo"
)

exams = [
    ExamRecord("Algoritmi e Protocolli per la Sicurezza", "0622720", "scritto", "obbligatoria", 30, 9, "2025-01-15", "Ingegneria Informatica"),
    ExamRecord("Intelligenza Artificiale", "0622730", "orale", "obbligatoria", 27, 9, "2025-02-10", "Ingegneria Informatica"),
    ExamRecord("Automazione", "0622740", "scritto", "obbligatoria", 18, 9, "2025-03-01", "Ingegneria Informatica")
]

validity = ValidityPeriod(
    issued_at=time.strftime("%Y-%m-%dT%H:%M:%S")
)

issuer = Issuer(
    issuer_id=u_rennes.university_id,
    name=u_rennes.official_name,
    location=u_rennes.location
)

cred = AcademicCredential(
    subject=subject,
    degree=degree,
    enrollment=enrollment,
    validity=validity,
    issuer=issuer,
    exams=exams
)

# ====== MISURA DIMENSIONI ======
serialized_cred = json.dumps(cred.to_dict()).encode("utf-8")
cred_size = sys.getsizeof(serialized_cred)

# Firma digitale
start = time.perf_counter()
signature = u_rennes.sign_message(serialized_cred)
end = time.perf_counter()
sign_time_ms = (end - start) * 1000

proof = Proof(
    signature_value=signature.hex(),
    verification_method=u_rennes.get_serialized_public_key()
)
cred.set_proof(proof)

signed_cred_size = sys.getsizeof(json.dumps(cred.to_dict()).encode("utf-8"))

# ====== MISURA TEMPI ======

# 1. Hash credenziale
start = time.perf_counter()
cred_hash = hashlib.sha256(serialized_cred).hexdigest()
end = time.perf_counter()
hash_time_ms = (end - start) * 1000

# 2. Verifica firma
start = time.perf_counter()
valid = mobility_ca.verify_signature(
    message=serialized_cred,
    signature=signature,
    certificate=u_rennes.get_certificate()
)
end = time.perf_counter()
verify_sign_time_ms = (end - start) * 1000

# 3. Calcolo Merkle Root
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

start = time.perf_counter()
merkle_root = MerkleTree(flat_attrs).get_root()
end = time.perf_counter()
merkle_root_time_ms = (end - start) * 1000

# 4. Verifica Merkle Proof (su un attributo)
attr_key, attr_val = flat_attrs[0]
merkle_proof = MerkleTree(flat_attrs).get_proof(attr_key)

start = time.perf_counter()
valid_proof = MerkleTree.verify_proof(attr_val, merkle_proof, merkle_root)
end = time.perf_counter()
verify_merkle_time_ms = (end - start) * 1000

# 5. Verifica stato di revoca del certificato
start = time.perf_counter()
cert_revoked = mobility_ca.is_certificate_revoked(u_rennes.get_certificate())
end = time.perf_counter()
revocation_check_time_ms = (end - start) * 1000

# 6. Verifica stato di accreditamento universitario
start = time.perf_counter()
accreditation_check = not mobility_ca._certificate_manager.is_revoked_by_university(u_rennes.university_id)
end = time.perf_counter()
accreditation_check_time_ms = (end - start) * 1000

# 7. Simulazione PBFT
blockchain = Blockchain(mobility_ca)
tx = Transaction(
    credential_hash=cred_hash,
    credential_unique_id="CAD-ALICE-ERASMUS-FR001",
    student_wallet_address=alice_wallet.get_wallet_address()
)
tx.sign_transaction(u_rennes.get_private_key())

start = time.perf_counter()
blockchain.add_block(
    transaction=tx,
    version="1.0",
    block_number=1,
    block_proposer_obj=u_rennes,
    attributes_merkle_root=merkle_root
)
end = time.perf_counter()
pbft_time_ms = (end - start) * 1000

# ====== STAMPA RISULTATI ======

print(f"\n Dimensione Credenziale (serializzata): {cred_size / 1024:.2f} KiB")
print(f" Dimensione Credenziale firmata: {signed_cred_size / 1024:.2f} KiB\n")

print(" Tempi di esecuzione (latenza locale):\n")
print(f" - Calcolo hash SHA256: {hash_time_ms:.3f} ms")
print(f" - Firma digitale (SHA256-RSA): {sign_time_ms:.3f} ms")
print(f" - Verifica firma digitale: {verify_sign_time_ms:.3f} ms")
print(f" - Calcolo Merkle Root: {merkle_root_time_ms:.3f} ms")
print(f" - Verifica Merkle Proof: {verify_merkle_time_ms:.3f} ms")
print(f" - Verifica revoca certificato: {revocation_check_time_ms:.3f} ms")
print(f" - Verifica accreditamento universitario: {accreditation_check_time_ms:.3f} ms")
print(f" - Simulazione consenso PBFT (Prepare + Commit): {pbft_time_ms:.3f} ms\n")

# ====== TEST: DIMENSIONI DELLE PRESENTAZIONI SELETTIVE ======
def presentation_sizes(student_wallet: StudentWallet, credential_id: str, attribute_labels: list):
    print("\n=== TEST DIMENSIONE PRESENTAZIONI SELETTIVE ===")
    print("Misuro la dimensione (in KiB) delle presentazioni JSON serializzate, generate con Merkle Proof.\n")

    for n in [1, 3, 6, 10]:
        if n > len(attribute_labels):
            continue  # evita test non validi

        fields_to_reveal = attribute_labels[:n]
        presentation = student_wallet.generate_presentation_proof(credential_id, fields_to_reveal)

        # Serializza la presentazione in JSON
        serialized = json.dumps(presentation, indent=2).encode("utf-8")
        size_kib = len(serialized) / 1024

        print(f"• {n} attributi rivelati → dimensione: {size_kib:.2f} KiB")

# Etichette che corrispondono ai campi rivelabili dal wallet
revealable_fields = [
    "studentId", "name", "dateOfBirth", "residence", "email",
    "courseName", "courseCode", "grade", "finalGrade", "thesisTitle"
]

# Chiave identificativa della credenziale in Alice
credential_id = "CAD-ALICE-ERASMUS-FR001"
alice_wallet.store_credential(credential_id, cred)

# Esegui test delle dimensioni
presentation_sizes(alice_wallet, credential_id, revealable_fields)

print(" Test completato con successo.\n")
