import json
from datetime import datetime, UTC

# Import delle strutture
from UniChain.structures.issuer import Issuer
from UniChain.structures.credential_subject import CredentialSubject
from UniChain.structures.enrollement import Enrollement
from UniChain.structures.degree import Degree
from UniChain.structures.validity_period import ValidityPeriod
from UniChain.structures.exam_record import ExamRecord
from UniChain.structures.optional_activity import OptionalActivity  # se lo hai creato
from UniChain.structures.proof import Proof

# Validator
from UniChain.utils.validator import Validator


def main():
    validator = Validator()

    try:
        # === Issuer ===
        issuer = Issuer(
            issuer_id="urn:unichain:it:unisa",
            name="Universita di Salerno",
            location="Fisciano"
        )

        # === Subject ===
        subject = CredentialSubject(
            validator=validator,
            student_id="STU987654",
            name="Luca Bianchi",
            date_of_birth="2001-03-12",
            residence="Napoli",
            phone_number="+393470000000",
            email="luca.bianchi@studenti.unisa.it"
        )

        # === Enrollement ===
        enrollement = Enrollement(
            academic_year=2023,
            regulation_year=2022,
            enrollment_date="2023-10-01",
            faculty="Ingegneria",
            course_name="Ingegneria Informatica",
            course_code="INF123",
            career_status="attivo"
        )

        # === Degree ===
        degree = Degree(
            title_name="Laurea Triennale in Ingegneria Informatica",
            degree_level="Laurea",
            graduation_date="2026-03-15",
            final_grade="110L",
            awarding_institution="Università di Salerno",
            thesis_title="Analisi di sistemi distribuiti",
            honors="Premio miglior tesi"
        )

        # === ValidityPeriod ===
        validity = ValidityPeriod(
            issued_at=datetime.now(UTC).isoformat(),
            expires_at=None
        )

        # === Exam Records ===
        exam1 = ExamRecord(
                course_name="Reti di calcolatori",
            course_code="RDC101",
            type_examination="orale",
            attendance="frequentato",
            grade=30,
            course_credits=9,
            date="2024-06-10",
            faculty="Ingegneria"
        )

        exam2 = ExamRecord(
            course_name="Algoritmi e strutture dati",
            course_code="ALG201",
            type_examination="scritto",
            attendance="frequentato",
            grade=28,
            course_credits=9,
            date="2024-07-01",
            faculty="Ingegneria"
        )

        exams = [exam1, exam2]

        # === Optional Activities ===
        activity1 = OptionalActivity(name="Tutoraggio Matematica", type_="tutorato", duration=20)
        activity2 = OptionalActivity(name="Hackathon UNISA", type_="competizione", duration=12)
        activities = [activity1, activity2]

        # === Proof (firma fittizia per il test) ===
        proof = Proof(signature_value="SIGN(H(CAD))")

        # === Composizione finale ===
        full_credential = {
            "issuer": issuer.to_dict(),
            "subject": subject.to_dict(),
            "enrollement": enrollement.to_dict(),
            "degree": degree.to_dict(),
            "validityPeriod": validity.to_dict(),
            "credentialSubject": [e.to_dict() for e in exams],
            "optionalActivites": [a.to_dict() for a in activities],
            "proof": proof.to_dict()
        }

        # === Stampa finale ===
        print("\nCredenziale accademica costruita con successo:\n")
        print(json.dumps(full_credential, indent=4))

    except ValueError as e:
        print(f"\nErrore di validazione: {e}")


if __name__ == "__main__":
    main()
