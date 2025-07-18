import uuid
import datetime
from typing import List, Optional, Dict


class CredentialUniChain:
    def __init__(
        self,
        validator,
        issuer: dict,
        subject: dict,
        enrollment: dict,
        degree: dict,
        credential_subject: List[dict],
        optional_activities: Optional[List[dict]] = None
    ):
        self.validator = validator
        self.credential_id = str(uuid.uuid4())
        self.issued_at = datetime.date.today().isoformat()
        self.expires_at = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()
        self.proof = None  # verrà inserito successivamente tramite firma

        # === Validazioni (minime) ===
        validator._validate_string(issuer["name"], "issuer.name")
        validator._validate_only_char(issuer["location"], "issuer.location")
        validator._validate_string(subject["id"], "subject.id")
        validator._validate_date(subject["dateOfBirth"], "subject.dateOfBirth")
        validator._validate_only_char(degree["degreeLevel"], "degree.degreeLevel")
        validator._validate_date(degree["graduationDate"], "degree.graduationDate")
        validator._validate_year(enrollment["academicYear"], "enrollment.academicYear")

        self.issuer = issuer
        self.subject = subject
        self.enrollment = enrollment
        self.degree = degree
        self.credential_subject = credential_subject
        self.optional_activities = optional_activities or []

    def set_proof(self, proof: dict):
        """Imposta il campo `proof` con firma e metadata"""
        self.proof = proof

    def to_dict(self) -> dict:
        return {
            "credential_id": self.credential_id,
            "issuer": self.issuer,
            "subject": self.subject,
            "enrollment": self.enrollment,
            "degree": self.degree,
            "validityPeriod": {
                "issuedAt": self.issued_at,
                "expiresAt": self.expires_at
            },
            "credentialSubject": self.credential_subject,
            "optionalActivities": self.optional_activities,
            "proof": self.proof
        }

    def get_flat_attributes(self) -> Dict[str, str]:
        """
        Converte la credenziale in una struttura piatta di attributi,
        utile per calcolare la Merkle Root.
        """
        flat = {}

        def flatten(section: str, data: dict):
            for k, v in data.items():
                flat[f"{section}.{k}"] = str(v)

        flatten("issuer", self.issuer)
        flatten("subject", self.subject)
        flatten("enrollment", self.enrollment)
        flatten("degree", self.degree)
        flatten("validityPeriod", {
            "issuedAt": self.issued_at,
            "expiresAt": self.expires_at
        })

        for i, exam in enumerate(self.credential_subject):
            flatten(f"credentialSubject.{i}", exam)

        for i, activity in enumerate(self.optional_activities):
            flatten(f"optionalActivities.{i}", activity)

        return flat

    def __str__(self):
        def format_dict(d: dict, indent=2):
            pad = " " * indent
            return "\n".join(f"{pad}{k}: {v}" for k, v in d.items())

        def format_list(lst: List[dict], title: str, indent=2):
            pad = " " * indent
            if not lst:
                return f"{pad}{title}: Nessuna"
            lines = [f"{pad}{title}:"]
            for i, item in enumerate(lst, 1):
                lines.append(f"{pad}  - {i}.")
                for k, v in item.items():
                    lines.append(f"{pad}    {k}: {v}")
            return "\n".join(lines)

        return (
            f"=== Credential UniChain ===\n"
            f"ID: {self.credential_id}\n"
            f"Rilascio: {self.issued_at} | Scadenza: {self.expires_at}\n\n"
            f"-- Issuer --\n{format_dict(self.issuer)}\n\n"
            f"-- Subject --\n{format_dict(self.subject)}\n\n"
            f"-- Enrollment --\n{format_dict(self.enrollment)}\n\n"
            f"-- Degree --\n{format_dict(self.degree)}\n\n"
            f"-- Exams --\n{format_list(self.credential_subject, 'Esami')}\n\n"
            f"-- Extra Activities --\n{format_list(self.optional_activities, 'Attività Extra')}"
        )
