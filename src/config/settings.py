from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FACULTY_IDS: dict[str, int] = {
        "ФКЯиК": 221,
        "ФАЯ": 202,
        "ФНЯ": 196,
        "ФРЯ": 222,
        "ПФ": 203,
        "ФМК": 193,
        "Магистратура": 217,
    }

    WEEK_TYPES: list[str] = ["currentWeek", "nextWeek", "thirdWeek", "fourthWeek"]

    EDUCATION_FORMS: dict[str, int] = {"Очная": 1, "Заочная": 2}
    
    class Config:
        env_file = ".env"

settings = Settings()
