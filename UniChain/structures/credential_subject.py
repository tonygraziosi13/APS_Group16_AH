from UniChain.utils.validator import Validator


class CredentialSubject:
    """
    Rappresenta i dati anagrafici dello studente a cui è intestata la credenziale.
    Include identificativo, nome, data di nascita, residenza, telefono ed email.
    """

    def __init__(
        self,
        student_id: str,
        name: str,
        date_of_birth: str,
        residence: str,
        phone_number: str,
        email: str,
        validator: Validator
    ):
        """
        Inizializza il soggetto della credenziale con i dati personali dello studente.
        Tutti i campi vengono validati tramite il Validator fornito.
        """
        validator.validate_string(student_id, "student_id")
        validator.validate_only_char(name, "name")
        validator.validate_date(date_of_birth, "date_of_birth")
        validator.validate_only_char(residence, "residence")
        validator.validate_telephone(phone_number, "phone_number")
        validator.validate_email(email, "email")

        self.student_id = student_id
        self.name = name
        self.date_of_birth = date_of_birth
        self.residence = residence
        self.phone_number = phone_number
        self.email = email

    def to_dict(self):
        """
        Serializza i dati dello studente in un dizionario JSON-compatibile.
        """
        return {
            "id": self.student_id,
            "name": self.name,
            "dateOfBirth": self.date_of_birth,
            "residence": self.residence,
            "numTelephone": self.phone_number,
            "email": self.email
        }
