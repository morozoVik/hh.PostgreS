import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


@dataclass
class DatabaseConfig:
    dbname: str = os.getenv("DB_NAME", "hh_vacancies")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", 5432))

    def __post_init__(self):
        """Вывод параметров для отладки"""
        print(f"DB Config: {self.dbname}, User: {self.user}")
        print(f"Password provided: {'Yes' if self.password else 'No'}")


@dataclass
class APIConfig:
    base_url: str = "https://api.hh.ru"
    user_agent: str = "HHVacancyParser/1.0 (ulb9@mail.ru)"
    timeout: int = 10


COMPANIES = [
    {"id": 1740, "name": "Яндекс"},
    {"id": 3529, "name": "Сбер"},
    {"id": 78638, "name": "Тинькофф"},
    {"id": 2748, "name": "Ростелеком"},
    {"id": 4181, "name": "ВКонтакте"},
    {"id": 907345, "name": "Ozon"},
    {"id": 1057, "name": "Касперский"},
    {"id": 49357, "name": "Магнит"},
    {"id": 64174, "name": "2ГИС"},
    {"id": 1122462, "name": "Skyeng"},
]
