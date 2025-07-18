from utils.validator import Validator


class ExamRecord:
    def __init__(self,
                 course_name: str,
                 course_code: str,
                 type_examination: str,
                 attendance: str,
                 grade: int,
                 course_credits: int,
                 date: str,
                 faculty: str):

        self.course_name = Validator.validate_string(course_name, "courseName")
        self.course_code = Validator.validate_string(course_code, "courseCode")
        self.type_examination = Validator.validate_only_char(type_examination, "typeExamination")
        self.attendance = Validator.validate_string(attendance, "attendance")
        self.grade = Validator.validate_vote(grade, "grade")
        self.course_credits = Validator.validate_integer(course_credits, "credits")
        self.date = Validator.validate_date(date, "date")
        self.faculty = Validator.validate_only_char(faculty, "faculty")

    def to_dict(self):
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
