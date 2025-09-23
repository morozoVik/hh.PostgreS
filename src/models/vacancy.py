from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Vacancy:
    """Модель вакансии"""

    id: int
    employer_id: int
    name: str
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    currency: Optional[str] = None
    area: Optional[str] = None
    published_at: Optional[datetime] = None
    experience: Optional[str] = None
    employment: Optional[str] = None
    schedule: Optional[str] = None
    requirement: Optional[str] = None
    responsibility: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_hh_data(cls, data: dict) -> "Vacancy":
        """Создать объект из данных API HH"""
        salary = data.get("salary")

        published_at = None
        if data.get("published_at"):
            published_at = cls._parse_date(data["published_at"])

        return cls(
            id=data.get("id"),
            employer_id=data.get("employer", {}).get("id"),
            name=data.get("name", ""),
            salary_from=salary.get("from") if salary else None,
            salary_to=salary.get("to") if salary else None,
            currency=salary.get("currency") if salary else None,
            area=data.get("area", {}).get("name") if data.get("area") else None,
            published_at=published_at,
            experience=(
                data.get("experience", {}).get("name")
                if data.get("experience")
                else None
            ),
            employment=(
                data.get("employment", {}).get("name")
                if data.get("employment")
                else None
            ),
            schedule=(
                data.get("schedule", {}).get("name") if data.get("schedule") else None
            ),
            requirement=data.get("snippet", {}).get("requirement"),
            responsibility=data.get("snippet", {}).get("responsibility"),
            url=data.get("alternate_url"),
        )

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """
        Парсит дату из различных форматов, которые может возвращать HH.ru
        """
        try:
            # Формат: 2025-09-23T16:10:21+0300 (без двоеточия в часовом поясе)
            if '+' in date_str and ':' not in date_str.split('+')[1]:
                # Добавляем двоеточие в часовой пояс: +0300 -> +03:00
                date_str = date_str[:-2] + ':' + date_str[-2:]

            # Формат: 2025-09-23T16:10:21Z (UTC)
            date_str = date_str.replace('Z', '+00:00')

            return datetime.fromisoformat(date_str)
        except ValueError as e:
            print(f"Ошибка парсинга даты '{date_str}': {e}")
            return None

    def get_avg_salary(self) -> Optional[float]:
        """Получить среднюю зарплату"""
        if self.salary_from and self.salary_to:
            return (self.salary_from + self.salary_to) / 2
        elif self.salary_from:
            return self.salary_from
        elif self.salary_to:
            return self.salary_to
        return None
