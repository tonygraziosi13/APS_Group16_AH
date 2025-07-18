import re
import datetime


class Validator:

    @staticmethod
    def validate_string(val, field):
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"{field} deve essere una stringa non vuota.")
        return val

    @staticmethod
    def validate_only_char(val, field):
        Validator.validate_string(val, field)
        if not re.fullmatch(r"[A-Za-zÀ-ÿ\s]+", val):
            raise ValueError(f"{field} deve contenere solo lettere.")
        return val

    @staticmethod
    def validate_date(val, field):
        try:
            datetime.date.fromisoformat(val)
            return val
        except Exception:
            raise ValueError(f"{field} deve essere in formato YYYY-MM-DD.")

    @staticmethod
    def validate_telephone(val, field):
        if not re.fullmatch(r"\+?[0-9\s\-]{7,15}", val):
            raise ValueError(f"{field} deve essere un numero di telefono valido.")
        return val

    @staticmethod
    def validate_email(val, field):
        if not re.fullmatch(r"^[\w.-]+@[\w.-]+\.\w+$", val):
            raise ValueError(f"{field} deve essere un indirizzo email valido.")
        return val

    @staticmethod
    def validate_year(val, field):
        current_year = datetime.date.today().year
        if not isinstance(val, int):
            raise ValueError(f"{field} deve essere un intero valido.")
        if not (1900 <= val <= current_year + 1):
            raise ValueError(f"{field} deve essere un anno tra 1900 e {current_year + 1}.")
        return val

    @staticmethod
    def validate_datetime(val, field):
        try:
            datetime.datetime.fromisoformat(val)
            return val
        except Exception:
            raise ValueError(f"{field} deve essere in formato ISO 8601 (es. YYYY-MM-DDTHH:MM:SS).")

    @staticmethod
    def validate_vote(val, field):
        if not isinstance(val, int):
            raise ValueError(f"{field} deve essere un numero intero.")
        if not (18 <= val <= 30):
            raise ValueError(f"{field} deve essere un voto tra 18 e 30.")
        return val

    @staticmethod
    def validate_integer(val, field):
        if not isinstance(val, int):
            raise ValueError(f"{field} deve essere un intero valido.")
        return val

    @staticmethod
    def validate_type_examination(val, field):
        allowed = {"scritto", "orale"}
        val = Validator.validate_string(val, field)
        if val.lower() not in allowed:
            raise ValueError(f"{field} deve essere 'scritto' o 'orale'.")
        return val



