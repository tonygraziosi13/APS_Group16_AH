from UniChain.structures.credential_subject import CredentialSubject
from UniChain.structures.degree import Degree
from UniChain.structures.enrollment import Enrollment
from UniChain.structures.exam_record import ExamRecord
from UniChain.structures.issuer import Issuer
from UniChain.structures.optional_activity import OptionalActivity
from UniChain.structures.validity_period import ValidityPeriod
from UniChain.structures.proof import Proof


class AcademicCredential:
    """
    Rappresenta una credenziale accademica digitale (CAD),
    strutturata secondo la specifica UniChain (WP1 - sezione 1.6).

    Contiene informazioni su:
    - Studente (credentialSubject)
    - Titolo di studio (degree)
    - Iscrizione e carriera (enrollment)
    - Periodo di validità (validityPeriod)
    - Istituzione emittente (issuer)
    - Esami sostenuti (exams)
    - Attività opzionali (optionalActivities)
    - Firma digitale (proof)
    """

    def __init__(self, subject: CredentialSubject, degree: Degree,
                 enrollment: Enrollment, validity: ValidityPeriod,
                 issuer: Issuer, exams: list[ExamRecord],
                 optional_activities: list[OptionalActivity] = None,
                 proof: Proof = None):
        self.credentialSubject = subject
        self.degree = degree
        self.enrollment = enrollment
        self.validityPeriod = validity
        self.issuer = issuer
        self.exams = exams
        self.optionalActivities = optional_activities or []
        self.proof = proof

    def set_proof(self, proof: Proof):
        """
        Imposta la firma digitale (proof) della credenziale.
        Da usare dopo aver calcolato hash e generato la firma.
        """
        self.proof = proof

    def to_dict(self):
        """
        Serializza la credenziale in un dizionario JSON-compatibile.
        Questo formato è utile per il calcolo dell’hash, per il Merkle Tree,
        e per l’invio verso il wallet o il sistema di verifica.
        """
        return {
            "credentialSubject": self.credentialSubject.to_dict(),
            "degree": self.degree.to_dict(),
            "enrollment": self.enrollment.to_dict(),
            "validityPeriod": self.validityPeriod.to_dict(),
            "issuer": self.issuer.to_dict(),
            "exams": [exam.to_dict() for exam in self.exams],
            "optionalActivities": [activity.to_dict() for activity in self.optionalActivities],
            "proof": self.proof.to_dict() if self.proof else None
        }
