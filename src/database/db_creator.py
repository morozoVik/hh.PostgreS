import psycopg2

from src.config import DatabaseConfig


class DBCreator:
    """Класс для создания базы данных и таблиц"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = None

    def create_tables(self) -> bool:
        """
        Создание таблиц в базе данных

        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            self.connection = psycopg2.connect(
                dbname=self.config.dbname,
                user=self.config.user,
                password=self.config.password,
                host=self.config.host,
                port=self.config.port,
            )

            cursor = self.connection.cursor()

            # Таблица employers
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS employers (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    area VARCHAR(100),
                    open_vacancies INTEGER,
                    site_url VARCHAR(255),
                    hh_url VARCHAR(255)
                )
            """
            )

            # Таблица vacancies
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    id INTEGER PRIMARY KEY,
                    employer_id INTEGER REFERENCES employers(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    currency VARCHAR(10),
                    area VARCHAR(100),
                    published_at TIMESTAMP,
                    experience VARCHAR(100),
                    employment VARCHAR(100),
                    schedule VARCHAR(100),
                    requirement TEXT,
                    responsibility TEXT,
                    url VARCHAR(255)
                )
            """
            )

            self.connection.commit()
            cursor.close()
            print("Таблицы созданы успешно")
            return True

        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            if self.connection:
                self.connection.close()
