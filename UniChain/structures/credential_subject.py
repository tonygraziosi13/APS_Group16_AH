from ..utils.validator import Validator


class CredentialSubject:
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
        return {
            "id": self.student_id,
            "name": self.name,
            "dateOfBirth": self.date_of_birth,
            "residence": self.residence,
            "numTelephone": self.phone_number,
            "e-mail": self.email
        }
