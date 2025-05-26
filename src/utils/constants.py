from enum import Enum


class Faculties(Enum):
    CHINESE = 221
    ENGLISH = 202
    GERMAN = 196
    ROMAN = 222
    TRANSLATORS =  203
    INTERNATIONAL_COMMUNICATIONS = 193
    MASTERS = 217


class EducationForms(Enum):
    FULL_TIME = 1
    PART_TIME = 2


WEEK_TYPES: list[str] = ["currentWeek", "nextWeek", "thirdWeek", "fourthWeek"]
