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

        return cls(
            id=data.get("id"),
            employer_id=data.get("employer", {}).get("id"),
            name=data.get("name", ""),
            salary_from=salary.get("from") if salary else None,
            salary_to=salary.get("to") if salary else None,
            currency=salary.get("currency") if salary else None,
            area=data.get("area", {}).get("name") if data.get("area") else None,
            published_at=(
                datetime.fromisoformat(data["published_at"].replace("Z", "+00:00"))
                if data.get("published_at")
                else None
            ),
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

    def get_avg_salary(self) -> Optional[float]:
        """Получить среднюю зарплату"""
        if self.salary_from and self.salary_to:
            return (self.salary_from + self.salary_to) / 2
        elif self.salary_from:
            return self.salary_from
        elif self.salary_to:
            return self.salary_to
        return None
