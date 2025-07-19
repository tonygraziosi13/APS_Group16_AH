from UniChain.moblityCA.mobilityCA import MobilityCA
from UniChain.university.university import University
from cryptography.hazmat.primitives import serialization

def main():
    print("\n--- Inizio simulazione accreditamento ---\n")

    # 1. Inizializza MobilityCA
    mobility_ca = MobilityCA()

    # 2. Università di Rennes genera chiavi e prepara richiesta
    print("[Université de Rennes] Generazione chiavi e richiesta accreditamento...\n")
    rennes = University(
        university_id="urn:univ:rennes",
        official_name="Université de Rennes",
        university_code="RENNES001",
        location="Rennes",
        mobility_ca=mobility_ca
    )

    # 3. Invio richiesta di accreditamento
    rennes.request_accreditation()

    # 4. Visualizza certificato ricevuto
    certificate = rennes.get_certificate()
    cert_pem = certificate.public_bytes(
        encoding=serialization.Encoding.PEM
    ).decode()

    print(f"\n📄 Certificato ricevuto (troncato):\n{cert_pem[:400]}...\n")

    # 5. MobilityCA pubblica il registro pubblico
    print("--- Registro pubblico attuale ---\n")
    registry = mobility_ca.get_public_registry()
    for entry in registry:
        print(f"- ID: {entry['university_id']}")
        print(f"  Revocato: {entry['revoked']}")
        print(f"  Chiave pubblica:\n{entry['public_key'][:200]}...\n")

    # 6. Simula revoca firmata da parte dell’università
    print("\n[Université de Rennes] Richiesta di revoca del certificato...\n")
    message = b"Revoke my certificate for maintenance"
    signature = rennes.sign_message(message)
    success = mobility_ca.receive_revocation_request(message, signature, rennes.university_id)

    print("\n✅ Risultato revoca firmata:", "Successo" if success else "Fallimento")

    # 7. Registro aggiornato
    print("\n--- Registro pubblico dopo revoca ---\n")
    registry = mobility_ca.get_public_registry()
    for entry in registry:
        print(f"- ID: {entry['university_id']}")
        print(f"  Revocato: {entry['revoked']}")
        print(f"  Chiave pubblica:\n{entry['public_key'][:200]}...\n")

    print("\n--- Fine simulazione accreditamento e revoca ---\n")

if __name__ == "__main__":
    main()
