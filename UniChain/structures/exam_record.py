from UniChain.utils.validator import Validator


class ExamRecord:
    """
    Rappresenta un esame superato dallo studente.
    Include informazioni su corso, tipo di esame, CFU, voto, data e facoltà.
    """

    def __init__(self,
                 course_name: str,
                 course_code: str,
                 type_examination: str,
                 attendance: str,
                 grade: int,
                 course_credits: int,
                 date: str,
                 faculty: str):
        """
        Inizializza un oggetto ExamRecord con i dettagli di un esame superato.
        Tutti i campi sono validati tramite Validator.
        """
        self.course_name = Validator.validate_string(course_name, "courseName")
        self.course_code = Validator.validate_string(course_code, "courseCode")
        self.type_examination = Validator.validate_only_char(type_examination, "typeExamination")
        self.attendance = Validator.validate_string(attendance, "attendance")
        self.grade = Validator.validate_vote(grade, "grade")
        self.course_credits = Validator.validate_integer(course_credits, "credits")
        self.date = Validator.validate_date(date, "date")
        self.faculty = Validator.validate_only_char(faculty, "faculty")

    def to_dict(self):
        """
        Serializza l'oggetto ExamRecord in un dizionario JSON compatibile.
        """
        return {
            "Type": "EsameSuperato",
            "courseName": self.course_name,
            "courseCode": self.course_code,
            "typeExamination": self.type_examination,
            "attendance": self.attendance,
            "grade": self.grade,
            "credits": self.course_credits,
            "date": self.date,
            "faculty": self.faculty
        }

    def __repr__(self):
        return f"ExamRecord({self.course_code}, grade={self.grade}, cfu={self.course_credits})"
