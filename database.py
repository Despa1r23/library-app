import psycopg2
from psycopg2 import sql
from datetime import datetime

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Подключение к базе данных"""
        try:
            self.connection = psycopg2.connect(
                host="localhost",
                database="library_db",
                user="library_user",
                password="807002"  # ЗАМЕНИ НА СВОЙ ПАРОЛЬ!
            )
            print("Успешное подключение к базе данных")
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
    
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
