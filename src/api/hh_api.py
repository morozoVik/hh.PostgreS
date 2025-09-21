import time
from typing import Any, Dict, List, Optional

import requests

from src.config import APIConfig


class HHAPI:
    """Класс для работы с API HeadHunter"""

    def __init__(self, config: APIConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.user_agent})

    def get_employer_info(self, employer_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о работодателе
        """
        url = f"{self.config.base_url}/employers/{employer_id}"

        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при получении данных работодателя {employer_id}: {e}")
            return None

    def get_employer_vacancies(
        self, employer_id: int, per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Получить вакансии работодателя
        """
        url = f"{self.config.base_url}/vacancies"
        params = {"employer_id": employer_id, "per_page": per_page, "page": 0}

        vacancies = []

        try:
            while True:
                response = self.session.get(
                    url, params=params, timeout=self.config.timeout
                )
                response.raise_for_status()
                data = response.json()

                vacancies.extend(data.get("items", []))

                # Проверяем, есть ли следующая страница
                if params["page"] >= data.get("pages", 1) - 1:
                    break

                params["page"] += 1
                time.sleep(0.1)  # Чтобы не превысить лимиты API

        except requests.RequestException as e:
            print(f"Ошибка при получении вакансий работодателя {employer_id}: {e}")

        return vacancies

    def get_all_data(self, company_ids: List[int]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Получить данные по всем компаниям
        """
        employers_data = []
        vacancies_data = []

        for company_id in company_ids:
            print(f"Получение данных для компании ID: {company_id}")

            # Получаем данные работодателя
            employer = self.get_employer_info(company_id)
            if employer:
                employers_data.append(employer)

                # Получаем вакансии работодателя
                vacancies = self.get_employer_vacancies(company_id)
                vacancies_data.extend(vacancies)

                print(f"Найдено {len(vacancies)} вакансий для {employer.get('name')}")

            time.sleep(0.2)  # Задержка между запросами

        return {"employers": employers_data, "vacancies": vacancies_data}
