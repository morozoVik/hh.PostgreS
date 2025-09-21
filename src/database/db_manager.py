from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import psycopg2

from src.config import DatabaseConfig


class DBManager:
    """Класс для управления базой данных вакансий"""

    def __init__(self, config: DatabaseConfig):
        self.config = config

    @contextmanager
    def _get_connection(self):
        """Контекстный менеджер для соединения с БД"""
        conn = None
        try:
            conn = psycopg2.connect(
                dbname=self.config.dbname,
                user=self.config.user,
                password=self.config.password,
                host=self.config.host,
                port=self.config.port,
            )
            yield conn
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def insert_employer(self, employer_data: Dict[str, Any]) -> bool:
        """Вставить данные работодателя в БД"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        INSERT INTO employers (id, name, description, area, open_vacancies, site_url, hh_url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            description = EXCLUDED.description,
                            area = EXCLUDED.area,
                            open_vacancies = EXCLUDED.open_vacancies,
                            site_url = EXCLUDED.site_url,
                            hh_url = EXCLUDED.hh_url
                    """,
                        (
                            employer_data["id"],
                            employer_data["name"],
                            employer_data.get("description"),
                            employer_data.get("area"),
                            employer_data.get("open_vacancies"),
                            employer_data.get("site_url"),
                            employer_data.get("hh_url"),
                        ),
                    )
                    conn.commit()
                    return True
                except Exception as e:
                    conn.rollback()
                    print(f"Ошибка при вставке работодателя: {e}")
                    return False

    def insert_vacancy(self, vacancy_data: Dict[str, Any]) -> bool:
        """Вставить данные вакансии в БД"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        INSERT INTO vacancies 
                        (id, employer_id, name, salary_from, salary_to, currency, area, 
                         published_at, experience, employment, schedule, requirement, responsibility, url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            salary_from = EXCLUDED.salary_from,
                            salary_to = EXCLUDED.salary_to,
                            currency = EXCLUDED.currency,
                            area = EXCLUDED.area,
                            published_at = EXCLUDED.published_at,
                            experience = EXCLUDED.experience,
                            employment = EXCLUDED.employment,
                            schedule = EXCLUDED.schedule,
                            requirement = EXCLUDED.requirement,
                            responsibility = EXCLUDED.responsibility,
                            url = EXCLUDED.url
                    """,
                        (
                            vacancy_data["id"],
                            vacancy_data["employer_id"],
                            vacancy_data["name"],
                            vacancy_data.get("salary_from"),
                            vacancy_data.get("salary_to"),
                            vacancy_data.get("currency"),
                            vacancy_data.get("area"),
                            vacancy_data.get("published_at"),
                            vacancy_data.get("experience"),
                            vacancy_data.get("employment"),
                            vacancy_data.get("schedule"),
                            vacancy_data.get("requirement"),
                            vacancy_data.get("responsibility"),
                            vacancy_data.get("url"),
                        ),
                    )
                    conn.commit()
                    return True
                except Exception as e:
                    conn.rollback()
                    print(f"Ошибка при вставке вакансии: {e}")
                    return False

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получить список всех компаний и количество вакансий у каждой компании
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        SELECT e.name, COUNT(v.id) as vacancy_count
                        FROM employers e
                        LEFT JOIN vacancies v ON e.id = v.employer_id
                        GROUP BY e.id, e.name
                        ORDER BY vacancy_count DESC
                    """
                    )
                    result = []
                    for row in cur.fetchall():
                        result.append({"company": row[0], "vacancies_count": row[1]})
                    return result
                except Exception as e:
                    print(f"Ошибка при получении данных: {e}")
                    return []

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получить список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        SELECT 
                            e.name as company_name,
                            v.name as vacancy_name,
                            v.salary_from,
                            v.salary_to,
                            v.currency,
                            v.url
                        FROM vacancies v
                        JOIN employers e ON v.employer_id = e.id
                        ORDER BY e.name, v.name
                    """
                    )
                    result = []
                    for row in cur.fetchall():
                        salary_info = None
                        if row[2] or row[3]:
                            salary_info = (
                                f"{row[2] or ''}-{row[3] or ''} {row[4] or ''}".strip()
                            )

                        result.append(
                            {
                                "company": row[0],
                                "vacancy": row[1],
                                "salary": salary_info,
                                "url": row[5],
                            }
                        )
                    return result
                except Exception as e:
                    print(f"Ошибка при получении вакансий: {e}")
                    return []

    def get_avg_salary(self) -> float:
        """
        Получить среднюю зарплату по вакансиям
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                        FROM vacancies 
                        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                    """
                    )
                    result = cur.fetchone()[0]
                    return float(result) if result else 0.0
                except Exception as e:
                    print(f"Ошибка при расчете средней зарплаты: {e}")
                    return 0.0

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям
        """
        avg_salary = self.get_avg_salary()

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        SELECT 
                            e.name as company_name,
                            v.name as vacancy_name,
                            v.salary_from,
                            v.salary_to,
                            v.currency,
                            v.url
                        FROM vacancies v
                        JOIN employers e ON v.employer_id = e.id
                        WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > %s
                        ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 DESC
                    """,
                        (avg_salary,),
                    )

                    result = []
                    for row in cur.fetchall():
                        salary_info = (
                            f"{row[2] or ''}-{row[3] or ''} {row[4] or ''}".strip()
                        )
                        result.append(
                            {
                                "company": row[0],
                                "vacancy": row[1],
                                "salary": salary_info,
                                "url": row[5],
                            }
                        )
                    return result
                except Exception as e:
                    print(f"Ошибка при получении вакансий: {e}")
                    return []

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получить список всех вакансий, в названии которых содержатся переданные слова
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        SELECT 
                            e.name as company_name,
                            v.name as vacancy_name,
                            v.salary_from,
                            v.salary_to,
                            v.currency,
                            v.url
                        FROM vacancies v
                        JOIN employers e ON v.employer_id = e.id
                        WHERE LOWER(v.name) LIKE %s
                        ORDER BY e.name, v.name
                    """,
                        (f"%{keyword.lower()}%",),
                    )

                    result = []
                    for row in cur.fetchall():
                        salary_info = None
                        if row[2] or row[3]:
                            salary_info = (
                                f"{row[2] or ''}-{row[3] or ''} {row[4] or ''}".strip()
                            )

                        result.append(
                            {
                                "company": row[0],
                                "vacancy": row[1],
                                "salary": salary_info,
                                "url": row[5],
                            }
                        )
                    return result
                except Exception as e:
                    print(f"Ошибка при поиске вакансий: {e}")
                    return []
