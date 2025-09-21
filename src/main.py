import os
import sys

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.api.hh_api import HHAPI
from src.config import COMPANIES, APIConfig, DatabaseConfig
from src.database.db_creator import DBCreator
from src.database.db_manager import DBManager
from src.models.employer import Employer
from src.models.vacancy import Vacancy


def setup_database() -> bool:
    """Настройка базы данных"""
    db_config = DatabaseConfig()
    db_creator = DBCreator(db_config)

    # Создаем базу данных (если используем PostgreSQL)
    if not create_postgres_database(db_config):
        return False

    # Создаем таблицы
    if not db_creator.create_tables():
        return False

    return True


def create_postgres_database(config: DatabaseConfig) -> bool:
    """
    Создание базы данных PostgreSQL

    Returns:
        True если успешно, False в случае ошибки
    """
    try:
        # Подключаемся к postgres для создания БД
        conn = psycopg2.connect(
            dbname="postgres",
            user=config.user,
            password=config.password,  # Добавляем пароль!
            host=config.host,
            port=config.port,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Проверяем существование БД
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config.dbname}'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {config.dbname}")
            print(f"База данных {config.dbname} создана успешно")
        else:
            print(f"База данных {config.dbname} уже существует")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        return False


def load_data_to_database() -> bool:
    """Загрузка данных в базу данных"""
    api_config = APIConfig()
    db_config = DatabaseConfig()

    # Получаем данные с API
    hh_api = HHAPI(api_config)
    company_ids = [company["id"] for company in COMPANIES]
    data = hh_api.get_all_data(company_ids)

    # Загружаем данные в БД
    db_manager = DBManager(db_config)

    # Загружаем работодателей
    employer_count = 0
    for employer_data in data["employers"]:
        employer = Employer.from_hh_data(employer_data)
        if db_manager.insert_employer(employer.__dict__):
            employer_count += 1

    # Загружаем вакансии
    vacancy_count = 0
    for vacancy_data in data["vacancies"]:
        vacancy = Vacancy.from_hh_data(vacancy_data)
        if db_manager.insert_vacancy(vacancy.__dict__):
            vacancy_count += 1

    print(f"Загружено {employer_count} работодателей и {vacancy_count} вакансий")
    return True


def user_interface():
    """Интерфейс взаимодействия с пользователем"""
    db_config = DatabaseConfig()
    db_manager = DBManager(db_config)

    while True:
        print("\n" + "=" * 50)
        print("МЕНЮ УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ ВАКАНСИЙ")
        print("=" * 50)
        print("1. Показать компании и количество вакансий")
        print("2. Показать все вакансии")
        print("3. Показать среднюю зарплату")
        print("4. Показать вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("6. Выход")
        print("=" * 50)

        choice = input("Выберите действие (1-6): ").strip()

        if choice == "1":
            companies = db_manager.get_companies_and_vacancies_count()
            print("\nКомпании и количество вакансий:")
            print("-" * 40)
            for company in companies:
                print(f"{company['company']}: {company['vacancies_count']} вакансий")

        elif choice == "2":
            vacancies = db_manager.get_all_vacancies()
            print(f"\nВсе вакансии ({len(vacancies)}):")
            print("-" * 80)
            for i, vacancy in enumerate(vacancies, 1):
                salary_info = vacancy["salary"] or "Не указана"
                print(f"{i}. {vacancy['company']} - {vacancy['vacancy']}")
                print(f"   Зарплата: {salary_info}")
                print(f"   Ссылка: {vacancy['url']}")
                if i < len(vacancies):
                    print("-" * 40)

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"\nСредняя зарплата по всем вакансиям: {avg_salary:.2f} RUB")

        elif choice == "4":
            vacancies = db_manager.get_vacancies_with_higher_salary()
            print(f"\nВакансии с зарплатой выше средней ({len(vacancies)}):")
            print("-" * 80)
            for i, vacancy in enumerate(vacancies, 1):
                print(f"{i}. {vacancy['company']} - {vacancy['vacancy']}")
                print(f"   Зарплата: {vacancy['salary']}")
                print(f"   Ссылка: {vacancy['url']}")
                if i < len(vacancies):
                    print("-" * 40)

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ").strip()
            if keyword:
                vacancies = db_manager.get_vacancies_with_keyword(keyword)
                print(f"\nНайдено вакансий по запросу '{keyword}': {len(vacancies)}")
                print("-" * 80)
                for i, vacancy in enumerate(vacancies, 1):
                    salary_info = vacancy["salary"] or "Не указана"
                    print(f"{i}. {vacancy['company']} - {vacancy['vacancy']}")
                    print(f"   Зарплата: {salary_info}")
                    print(f"   Ссылка: {vacancy['url']}")
                    if i < len(vacancies):
                        print("-" * 40)
            else:
                print("Ключевое слово не может быть пустым!")

        elif choice == "6":
            print("Выход из программы...")
            break

        else:
            print("Неверный выбор! Пожалуйста, выберите от 1 до 6.")

        input("\nНажмите Enter для продолжения...")


def main():
    """Основная функция программы"""
    print("Запуск программы по сбору вакансий с HH.ru")

    # Настройка базы данных
    print("Настройка базы данных...")
    if not setup_database():
        print("Ошибка при настройке базы данных!")
        return

    # Загрузка данных
    print("Загрузка данных с HH.ru...")
    if not load_data_to_database():
        print("Ошибка при загрузке данных!")
        return

    # Запуск интерфейса
    user_interface()


if __name__ == "__main__":
    main()
