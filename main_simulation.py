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
print("[Fase 1] ACCREDITAMENTO DI 4 UNIVERSITÀ PRESSO UniChain\n")

print("[Fase 1.1] UNIVERSITÉ DE RENNES\n")
mobility_ca = MobilityCA()
u_rennes = University("urn:rennes", "Université de Rennes", "FR-REN001", "Francia", mobility_ca)
print("Coppia di chiavi RSA generata localmente da U_RENNES.")
print("Chiave pubblica pk_UNI:", u_rennes.get_serialized_public_key())

print("\n[Fase 1.2] UNIVERSITÉ DE RENNES: RICHIESTA DI ACCREDITAMENTO A MobilityCA\n")
u_rennes.request_accreditation()

print("\nMobilityCA ha verificato i dati ricevuti e rilasciato un MUC (Mobility University Certificate) firmato digitalmente.")
print("Il MUC è stato archiviato sia dalla MobilityCA sia localmente da U_RENNES.")

u_salerno = University("urn:unisa", "Università di Salerno", "IT-SAL001", "Italia", mobility_ca)
u_bologna = University("urn:unibo", "Università di Bologna", "IT-BO001", "Italia", mobility_ca)
u_lisboa = University("urn:ulisboa", "Universidade de Lisboa", "PT-LIS001", "Portogallo", mobility_ca)

for u in [u_salerno, u_bologna, u_lisboa]:
    u.request_accreditation()

# === [Fase 1.3] Imposta la rete di peer (PBFT)
all_universities = [u_rennes, u_salerno, u_bologna, u_lisboa]
for u in all_universities:
    u.set_peers([peer for peer in all_universities if peer != u])

# === [FASE 1.4] STAMPA DEL REGISTRO PUBBLICO ===
print("\n[Fase 1.4] REGISTRO PUBBLICO DELLE UNIVERSITÀ ACCREDITATE\n")
registry = mobility_ca.get_public_registry()

for i, entry in enumerate(registry, 1):
    print(f"Università #{i}")
    print(f"   - ID: {entry['university_id']}")
    print(f"   - Stato revoca MUC: {'REVOCATO' if entry['revoked'] else 'ATTIVO'}")
    print(f"   - pk_UNI:\n     {entry['public_key']}")
    print()


# === [FASE 2] AUTENTICAZIONE FEDERATA DI ALICE TRAMITE SPID ===
print("\n[Fase 2.0] ALICE ACCEDE AL PORTALE DI U_RENNES TRAMITE AUTENTICAZIONE FEDERATA")

print("Alice effettua l'accesso al portale dell’università (Service Provider),")
print("utilizzando un Identity Provider federato (es. SPID o CIE ID).")
print("L’autenticazione ha successo e viene creata una sessione HTTPS sicura.")
print("Alice è ora autenticata e può accedere ai servizi universitari, inclusa la richiesta del proprio CAD.\n")

alice_wallet = StudentWallet("Alice")

credential_subject = CredentialSubject(
    student_id="8742",
    name="Alice Rossi",
    date_of_birth="2002-07-11",
    residence="Salerno",
    phone_number="+393331234567",
    email="alice.rossi@studenti.it",
    validator = u_rennes.mobility_ca.get_validator()  # usa validator condiviso
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

degree = Degree(
    title_name="Laurea in Ingegneria Informatica",
    degree_level="triennale",
    graduation_date="2024-09-15",
    final_grade="100",
    awarding_institution=u_salerno.official_name,
    thesis_title="UN SISTEMA PER LA GESTIONE DI NOTIFICHE WEB PUSH",
    honors=""
)

exams = [
    ExamRecord("Algoritmi e Protocolli per la Sicurezza", "0622720", "scritto", "obbligatoria", 30, 9, "2025-01-15", "Ingegneria Informatica"),
    ExamRecord("Intelligenza Artificiale", "0622730", "orale", "obbligatoria", 27, 9, "2025-02-10", "Ingegneria Informatica"),
    ExamRecord("Automazione", "0622740", "scritto", "obbligatoria", 18, 9, "2025-03-01", "Ingegneria Informatica")
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


# === [FASE 3] EMISSIONE, FIRMA E CONSEGNA DELLA CREDENZIALE ===
print("\n[Fase 3] U_RENNES EMETTE IL CAD, LO FIRMA DIGITALMENTE (Sign) E LO CONSEGNA AD ALICE\n")

# Serializzazione e firma
print("Serializzazione della credenziale accademica digitale (CAD)...")
serialized = str(cred.to_dict()).encode("utf-8")
print("Calcolo del Sign (firma digitale) della credenziale...")

signature = u_rennes.sign_message(serialized)

print("Sign generato da U_RENNES con sk_UNI.")
print(f"Sign (SHA256-RSA): {signature.hex()[:64]}...")

# Inserimento del proof nella credenziale
proof = Proof(
    signature_value=signature.hex(),
    verification_method=u_rennes.get_serialized_public_key()
)
cred.set_proof(proof)

print("Inserimento del Sign e della pk_UNI nella struttura del CAD.")

# Invio della credenziale ad Alice
credential_id = "CAD-ALICE-ERASMUS-FR001"
alice_wallet.store_credential(credential_id, cred)

print("Il CAD è stato consegnato in modo sicuro al Wallet Digitale di Alice.")
print("Alice ha ricevuto e memorizzato il CAD nel proprio Wallet Digitale.\n")


# === [FASE 4] ANCORAGGIO DEL CAD SULLA BLOCKCHAIN ===
print("\n[Fase 4] ANCORAGGIO DEL CAD SULLA BLOCKCHAIN UniChain\n")

# Step 1 – Inizializza la blockchain
blockchain = Blockchain(mobility_ca)
print("Blockchain UniChain inizializzata con blocco di genesi.")

# Step 2 – Calcola CredentialHash del CAD
cred_hash = hashlib.sha256(str(cred.to_dict()).encode()).hexdigest()
wallet_address = alice_wallet.get_wallet_address()
print("CredentialHash calcolato per il CAD.")
print(f"   - CredentialHash: {cred_hash}")
print(f"   - studentWalletAddress di Alice: {wallet_address}")

# Step 3 – Crea Transaction e firma con sk_UNI
tx = Transaction(
    credential_hash=cred_hash,
    credential_unique_id=credential_id,
    student_wallet_address=wallet_address
)
tx.sign_transaction(u_rennes.get_private_key())
print("TransactionType: EMISSIONE, firmata con sk_UNI.")
print(f"   - Hash della Transaction: {tx.transaction_hash}")
print(f"   - Sign (SHA256-RSA): {tx.signature[:64]}...")

# Step 4 – Calcola Merkle Root degli attributi
print("\nCalcolo della Merkle Root (Merkle Tree degli attributi del CAD)...")
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
print(f"   - Merkle Root calcolata: {merkle_root}")

# Step 5 – Aggiunge blocco alla blockchain
print("\nCreazione del blocco e firma del payload contenente il CAD...")
blockchain.add_block(
    transaction=tx,
    version="1.0",
    block_number=1,
    block_proposer_obj=u_rennes,
    attributes_merkle_root=merkle_root
)

# Step 6 – Stampa Mobility Trust Ranking aggiornato
mobility_ca.get_mobility_trust_ranking([u_rennes, u_salerno, u_bologna, u_lisboa])

# Step 7 – Verifica integrità
if blockchain.is_chain_valid():
    print("La blockchain UniChain è valida e coerente.")
else:
    print("Errore: la blockchain contiene blocchi non validi.")


# === [FASE 5] PRESENTAZIONE SELETTIVA A UNISA ===
print("\n[Fase 5] ALICE ACCEDE AL PORTALE DI UNISA TRAMITE AUTENTICAZIONE FEDERATA")

print("Alice accede al portale dell’università (Service Provider) tramite un Identity Provider federato (es. SPID o CIE ID).")
print("L’autenticazione federata ha successo e viene stabilita una sessione HTTPS sicura.")
print("Alice è ora autenticata e può accedere ai servizi di riconoscimento crediti.\n")

print("[Fase 5.1] ALICE PRESENTA UNA VERSIONE RIDOTTA DEL CAD A UNISA PER IL RICONOSCIMENTO CREDITI\n")

reveal_fields = ["courseName", "courseCode", "grade"]
presentation_proof = alice_wallet.generate_presentation_proof(credential_id, reveal_fields)

verifier = Verifier(blockchain)

# === STEP 1: Verifica firma di Alice ===
print("Step 1 – Verifica del Sign di Alice sulla Merkle Root...")
is_signature_valid = verifier.verify_student_signature(
    merkle_root=presentation_proof["merkleRoot"],
    signature_hex=presentation_proof["signature"],
    public_key_pem=presentation_proof["publicKey"]
)
print(f"    -Sign di Alice: {'VALIDA' if is_signature_valid else 'NON VALIDA'}\n")

# === STEP 2: Verifica Merkle Root sulla blockchain ===
print("Step 2 – Verifica della Merkle Root del CAD sulla blockchain UniChain...")
is_root_on_chain = verifier.check_merkle_root_on_chain(credential_id, presentation_proof["merkleRoot"])
print(f"    -Merkle Root sulla blockchain: {'TROVATA' if is_root_on_chain else 'NON TROVATA'}\n")

# === STEP 3: Verifica che la credenziale non sia stata revocata ===
print("Step 3 – Verifica dello stato di revoca del CAD...")
is_not_revoked = verifier.check_revocation_status(credential_id)
print(f"    -RevocationStatus del CAD: {'NON REVOCATA' if is_not_revoked else 'REVOCATA'}\n")

# === STEP 4: Verifica crittografica Merkle Proof per ciascun attributo ===
print("Step 4 – Verifica della Merkle Proof per ogni attributo rivelato:\n")
for label, value in presentation_proof["revealedAttributes"].items():
    proof = presentation_proof["merkleProofs"][label]
    print(f"    Attributo rivelato: {label}")
    print(f"     -Valore dichiarato: {value}")
    is_valid = verifier.verify_merkle_proof(value, proof, presentation_proof["merkleRoot"])
    print(f"     -Merkle Proof: {'VALIDA' if is_valid else 'NON VALIDA'}\n")

# === STEP 5: Esito finale ===
print("[RISULTATO FINALE] Verifica della presentazione selettiva del CAD:")
if is_signature_valid and is_root_on_chain and is_not_revoked:
    print("Verifica superata: Alice è autenticata, il CAD è integro e verificabile.\n")
else:
    print("Verifica fallita: uno o più controlli sul CAD non sono stati superati.\n")


# === [SCENARIO 1] REVOCA DELLA CREDENZIALE DI ALICE ===
print("\n[Fase 6] U_RENNES ESEGUE LA REVOCA DEL CAD DI ALICE\n")

# Parametri per la revoca
revoked_credential_id = credential_id
revoked_credential_hash = cred_hash
revoked_wallet_address = wallet_address

# Creazione della transazione di revoca
revocation_tx = Transaction(
    credential_hash=revoked_credential_hash,
    credential_unique_id=revoked_credential_id,
    student_wallet_address=revoked_wallet_address,
    revocation_status=True,
    transaction_type="REVOCA"
)
revocation_tx.sign_transaction(u_rennes.get_private_key())

print("TransactionType: REVOCA creata e firmata con sk_UNI.")
print(f"   - Hash della Transaction di revoca: {revocation_tx.transaction_hash}")
print(f"   - Sign (SHA256-RSA): {revocation_tx.signature[:64]}...")

# Calcolo Merkle Root per la revoca (opzionale)
print("\nCalcolo della Merkle Root del CAD da revocare...")
flat_attrs_revocation = []
def flatten_revocation(prefix, val):
    if isinstance(val, dict):
        for k, v in val.items():
            flatten_revocation(f"{prefix}.{k}", v)
    elif isinstance(val, list):
        for i, v in enumerate(val):
            flatten_revocation(f"{prefix}[{i}]", v)
    else:
        flat_attrs_revocation.append((prefix, str(val)))

flatten_revocation("credential", cred.to_dict())
merkle_root_revocation = MerkleTree(flat_attrs_revocation).get_root()
print(f"   - Merkle Root per revoca: {merkle_root_revocation}")

# Creazione e firma del blocco di revoca
print("\nCreazione del blocco contenente la revoca e firma del payload...")
blockchain.add_block(
    transaction=revocation_tx,
    version="1.0",
    block_number=len(blockchain.chain),
    block_proposer_obj=u_rennes,
    attributes_merkle_root=merkle_root_revocation
)

print("Blocco di revoca del CAD aggiunto alla blockchain UniChain.")

# Stampa Mobility Trust Ranking aggiornato
mobility_ca.get_mobility_trust_ranking([u_rennes, u_salerno, u_bologna, u_lisboa])

# === [SCENARIO 1] TEST DOPO LA REVOCA: ALICE PROVA A PRESENTARE LA CREDENZIALE ===
print("\n[Fase 7] TEST DOPO LA REVOCA: ALICE PROVA A PRESENTARE IL CAD A UNISA\n")

reveal_fields_after_revocation = ["courseName", "courseCode", "grade"]
presentation_proof_after_revocation = alice_wallet.generate_presentation_proof(credential_id, reveal_fields_after_revocation)

# === STEP 1: Verifica firma di Alice ===
print("Step 1 – Verifica del Sign di Alice sulla Merkle Root (post-revoca)...")
is_signature_valid_after_revocation = verifier.verify_student_signature(
    merkle_root=presentation_proof_after_revocation["merkleRoot"],
    signature_hex=presentation_proof_after_revocation["signature"],
    public_key_pem=presentation_proof_after_revocation["publicKey"]
)
print(f"    -Sign di Alice: {'VALIDA' if is_signature_valid_after_revocation else 'NON VALIDA'}\n")

# === STEP 2: Verifica Merkle Root sulla blockchain ===
print("Step 2 – Verifica della Merkle Root del CAD su UniChain...")
is_root_on_chain_after_revocation = verifier.check_merkle_root_on_chain(credential_id, presentation_proof_after_revocation["merkleRoot"])
print(f"    -Merkle Root sulla blockchain: {'TROVATA' if is_root_on_chain_after_revocation else 'NON TROVATA'}\n")

# === STEP 3: Verifica che la credenziale non sia stata revocata ===
print("Step 3 – Verifica RevocationStatus del CAD...")
is_not_revoked_after_revocation = verifier.check_revocation_status(credential_id)
print(f"    -RevocationStatus del CAD: {'NON REVOCATA' if is_not_revoked_after_revocation else 'REVOCATA'}\n")

# === STEP 4: Esito finale ===
print("[RISULTATO FINALE] Verifica della presentazione del CAD dopo la revoca:")
if is_signature_valid_after_revocation and is_root_on_chain_after_revocation and is_not_revoked_after_revocation:
    print("Verifica superata: il CAD è integro e verificabile.\n")
else:
    print("Verifica fallita: il CAD è stato revocato o uno dei controlli crittografici non è stato superato.\n")


# === [SCENARIO 2] REVOCA DELL'ACCREDITAMENTO DI U_RENNES DA PARTE DELLA MOBILITY CA ===
print("\n[Fase 8] MOBILITYCA REVOCA IL MUC DI U_RENNES\n")

# Simuliamo la revoca del certificato dell'università U_RENNES
certificate_u_rennes = u_rennes.get_certificate()

# Controllo che il certificato sia valido prima della revoca
is_cert_revoked_before = mobility_ca.is_certificate_revoked(certificate_u_rennes)
print(f"   - Stato del MUC prima della revoca: {'REVOCATO' if is_cert_revoked_before else 'VALIDO'}")

# Revoca del certificato
mobility_ca.revoke_certificate(u_rennes.university_id)
print(f"   - MUC di U_RENNES revocato da MobilityCA.")

# Verifica stato del certificato dopo la revoca
is_cert_revoked_after = mobility_ca.is_certificate_revoked(certificate_u_rennes)
print(f"   - Stato del MUC dopo la revoca: {'REVOCATO' if is_cert_revoked_after else 'VALIDO'}")


# === [SCENARIO 2] TEST DOPO LA REVOCA DEL CERTIFICATO DELL’UNIVERSITÀ ===
print("\n[Fase 9] Verifica di un CAD emesso da U_RENNES dopo la revoca del suo MUC\n")

# Alice prova a presentare la credenziale emessa da U_RENNES a UNISA
reveal_fields_cert_revoked = ["courseName", "courseCode", "grade"]
presentation_proof_cert_revoked = alice_wallet.generate_presentation_proof(credential_id, reveal_fields_cert_revoked)

# STEP 1: Verifica firma di Alice sulla Merkle Root
print("Step 1 – Verifica del Sign di Alice sulla Merkle Root...")
is_signature_valid_cert_revoked = verifier.verify_student_signature(
    merkle_root=presentation_proof_cert_revoked["merkleRoot"],
    signature_hex=presentation_proof_cert_revoked["signature"],
    public_key_pem=presentation_proof_cert_revoked["publicKey"]
)
print(f"    -Sign di Alice: {'VALIDA' if is_signature_valid_cert_revoked else 'NON VALIDA'}\n")

# STEP 2: Verifica Merkle Root sulla blockchain
print("Step 2 – Verifica della Merkle Root del CAD su UniChain...")
is_root_on_chain_cert_revoked = verifier.check_merkle_root_on_chain(credential_id, presentation_proof_cert_revoked["merkleRoot"])
print(f"    -Merkle Root sulla blockchain: {'TROVATA' if is_root_on_chain_cert_revoked else 'NON TROVATA'}\n")

# STEP 3: Verifica che il certificato dell’università non sia stato revocato
print("Step 3 – Verifica dello stato del MUC dell’università emittente...")
university_certificate = u_rennes.get_certificate()
is_university_cert_revoked = mobility_ca.is_certificate_revoked(university_certificate)
print(f"    -MUC dell’università: {'REVOCATO' if is_university_cert_revoked else 'VALIDO'}\n")

# STEP 4: Esito finale
print("[RISULTATO FINALE] Verifica con MUC universitario revocato:")
if is_signature_valid_cert_revoked and is_root_on_chain_cert_revoked and not is_university_cert_revoked:
    print("Verifica superata: il CAD è integro e il MUC dell’università è valido.\n")
else:
    print("Verifica fallita: il MUC dell’università è REVOCATO o uno dei controlli crittografici non è stato superato.\n")


# === RANKING MTP FINALE ===
print("\n[Fase 10] MOBILITY TRUST RANKING (MTP) AGGIORNATO\n")
mobility_ca.get_mobility_trust_ranking([u_rennes, u_salerno, u_bologna, u_lisboa])

