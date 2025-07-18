from utils.validator import Validator

class Enrollement:
    def __init__(
        self,
        academic_year: int,
        regulation_year: int,
        enrollment_date: str,
        faculty: str,
        course_name: str,
        course_code: str,
        career_status: str
    ):
        self.academic_year = Validator.validate_year(academic_year, "academicYear")
        self.regulation_year = Validator.validate_year(regulation_year, "regulationYear")
        self.enrollment_date = Validator.validate_date(enrollment_date, "enrollmentDate")
        self.faculty = Validator.validate_only_char(faculty, "faculty")
        self.course_name = Validator.validate_string(course_name, "courseName")
        self.course_code = Validator.validate_string(course_code, "courseCode")
        self.career_status = Validator.validate_string(career_status, "careerStatus")

    def to_dict(self):
        return {
            "academicYear": self.academic_year,
            "regulationYear": self.regulation_year,
            "enrollmentDate": self.enrollment_date,
            "faculty": self.faculty,
            "courseName": self.course_name,
            "courseCode": self.course_code,
            "careerStatus": self.career_status
        }
