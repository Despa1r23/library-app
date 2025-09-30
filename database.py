import psycopg2
from psycopg2 import sql
from datetime import datetime
import os  # Добавляем импорт для работы с переменными окружения

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Подключение к базе данных"""
        try:
            # Берем пароль из переменной окружения DB_PASSWORD
            # Если переменная не установлена, используем пустую строку
            db_password = os.getenv("DB_PASSWORD", "")
            
            self.connection = psycopg2.connect(
                host="localhost",
                database="library_db",
                user="library_user",
                password=db_password  # Используем переменную окружения
            )
            print("Успешное подключение к базе данных")
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            print("Проверьте:")
            print("1. Запущен ли PostgreSQL? (sudo systemctl status postgresql)")
            print("2. Установлена ли переменная окружения DB_PASSWORD?")
            print("3. Существует ли база данных library_db и пользователь library_user?")
    
    def get_all_books(self):
        """Получить все книги"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, author, title, is_read, date_read, created_at 
                    FROM books 
                    ORDER BY created_at DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении книг: {e}")
            return []
    
    def add_book(self, author, title):
        """Добавить новую книгу"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO books (author, title) 
                    VALUES (%s, %s) 
                    RETURNING id
                """, (author, title))
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Ошибка при добавлении книги: {e}")
            return False
    
    def mark_as_read(self, book_id, is_read=True):
        """Отметить книгу как прочитанную/непрочитанную"""
        try:
            with self.connection.cursor() as cursor:
                if is_read:
                    cursor.execute("""
                        UPDATE books 
                        SET is_read = TRUE, date_read = %s 
                        WHERE id = %s
                    """, (datetime.now().date(), book_id))
                else:
                    cursor.execute("""
                        UPDATE books 
                        SET is_read = FALSE, date_read = NULL 
                        WHERE id = %s
                    """, (book_id,))
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Ошибка при изменении статуса книги: {e}")
            return False
    
    def update_read_date(self, book_id, new_date):
        """Обновить дату прочтения книги"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE books 
                    SET date_read = %s, is_read = TRUE
                    WHERE id = %s
                """, (new_date, book_id))
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Ошибка при обновлении даты прочтения: {e}")
            return False
    
    def close(self):
        """Закрыть соединение с базой данных"""
        if self.connection:
            self.connection.close()
