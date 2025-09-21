from dataclasses import dataclass
from typing import Optional


@dataclass
class Employer:
    """Модель работодателя"""

    id: int
    name: str
    description: Optional[str] = None
    area: Optional[str] = None
    open_vacancies: Optional[int] = None
    site_url: Optional[str] = None
    hh_url: Optional[str] = None

    @classmethod
    def from_hh_data(cls, data: dict) -> "Employer":
        """Создать объект из данных API HH"""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description"),
            area=data.get("area", {}).get("name") if data.get("area") else None,
            open_vacancies=data.get("open_vacancies"),
            site_url=data.get("site_url"),
            hh_url=data.get("alternate_url"),
        )
