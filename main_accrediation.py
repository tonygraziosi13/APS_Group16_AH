from moblityCA.certificate_manager import CertificateManager
from university.university import University
from cryptography.hazmat.primitives.asymmetric import rsa

def main():
    # MobilityCA: genera chiavi e certificatore
    ca_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_public = ca_private.public_key()
    mobility_ca = CertificateManager(private_key=ca_private, public_key=ca_public)

    # Università
    rennes = University(
        university_id="https://univ-rennes.fr",
        official_name="Université de Rennes",
        university_code="ERASMUS-RENNES-FR01",
        location="Rennes",
        mobility_ca=mobility_ca
    )

    # Accredita
    rennes.request_accreditation()

    # Stampa registro pubblico
    print("\n📜 Registro pubblico delle università accreditate:")
    for entry in mobility_ca.get_public_registry():
        print(f"- ID: {entry['university_id']}, Revocato: {entry['revoked']}\n{entry['public_key']}")

    # Simula revoca firmata
    print("\n✉️ Simulazione richiesta di revoca firmata:")
    revoke_data = rennes.generate_revocation_request("Disattivazione volontaria")
    valid = mobility_ca.verify_signature(
        revoke_data["message"],
        revoke_data["signature"],
        revoke_data["certificate"]
    )
    if valid:
        mobility_ca.revoke_certificate(rennes.university_id)

    # Stampa registro aggiornato
    print("\n📜 Registro aggiornato:")
    for entry in mobility_ca.get_public_registry():
        print(f"- ID: {entry['university_id']}, Revocato: {entry['revoked']}\n{entry['public_key']}")

if __name__ == "__main__":
    main()
