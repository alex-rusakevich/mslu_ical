from enum import IntEnum


class Faculties(IntEnum):
    CHINESE = 221
    ENGLISH = 202
    GERMAN = 196
    ROMAN = 222
    TRANSLATORS =  203
    INTERNATIONAL_COMMUNICATIONS = 193
    MASTERS = 217


class EducationForms(IntEnum):
    FULL_TIME = 1
    PART_TIME = 2


WEEK_TYPES: list[str] = ["currentWeek", "nextWeek", "thirdWeek", "fourthWeek"]
