from UniChain.utils.validator import Validator


class Degree:
    """
    Rappresenta il titolo di studio conseguito, parte della credenziale accademica.
    Include informazioni come nome del titolo, livello, voto finale, ente erogatore e tesi (facoltativa).
    """

    def __init__(self,
                 title_name: str,
                 degree_level: str,
                 graduation_date: str,
                 final_grade: str,
                 awarding_institution: str,
                 thesis_title: str = None,
                 honors: str = None):
        """
        Inizializza un oggetto Degree con i dettagli del titolo di studio.
        I campi sono validati tramite la classe Validator.
        """
        self.title_name = Validator.validate_string(title_name, "titleName")
        self.degree_level = Validator.validate_only_char(degree_level, "degreeLevel")
        self.graduation_date = Validator.validate_date(graduation_date, "graduationDate")
        self.final_grade = Validator.validate_string(final_grade, "finalGrade")
        self.awarding_institution = Validator.validate_string(awarding_institution, "awardingInstitution")

        self.thesis_title = Validator.validate_string(thesis_title, "thesisTitle") if thesis_title else None
        self.honors = Validator.validate_string(honors, "honors") if honors else None

    def to_dict(self) -> dict:
        """
        Serializza l’oggetto Degree in un dizionario JSON-compatibile.
        Include solo i campi opzionali se presenti.
        """
        data = {
            "titleName": self.title_name,
            "degreeLevel": self.degree_level,
            "graduationDate": self.graduation_date,
            "finalGrade": self.final_grade,
            "awardingInstitution": self.awarding_institution,
        }

        if self.thesis_title:
            data["thesisTitle"] = self.thesis_title
        if self.honors:
            data["honors"] = self.honors

        return data

    def __repr__(self):
        return f"Degree({self.title_name}, {self.degree_level}, {self.final_grade})"
