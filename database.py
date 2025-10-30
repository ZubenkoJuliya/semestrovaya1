import sqlite3
import os
from datetime import datetime


class SQLiteDatabase:
    def __init__(self, db_path="database/database.sqlite"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        #Инициализация базы данных
        # Создаем папку если нет
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Проверяем существует ли файл базы данных
        if not os.path.exists(self.db_path):
            print("База данных не найдена. Запустите create_database.py для создания.")

    def get_connection(self):
        #Получение соединения с базой данных
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Чтобы получать строки как словари
        return conn

    def get_categories(self):
        #Получить все категории из базы данных
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT id, name, icon FROM categories ORDER BY name')
            categories = [(row['id'], row['name'], row['icon']) for row in cursor.fetchall()]

            conn.close()
            print(f"Загружено категорий: {len(categories)}")
            return categories

        except Exception as e:
            print(f"Ошибка чтения категорий: {e}")
            return []

    def add_password(self, category_id, website, username, encrypted_password, notes):
        #Добавить новый пароль в базу данных
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO passwords (category_id, website, username, encrypted_password, notes, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
            category_id, website, username, encrypted_password, notes, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            conn.commit()
            conn.close()

            print(f"Успешно добавлен пароль: {website}")
            return True

        except Exception as e:
            print(f"Ошибка добавления пароля: {e}")
            return False

    def get_all_passwords(self):
        #Получить все пароли с информацией о категориях
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT p.id, c.name as category, p.website, p.username, 
                       p.encrypted_password, p.notes, p.created_date
                FROM passwords p
                JOIN categories c ON p.category_id = c.id
                ORDER BY p.website
            ''')

            result = []
            for row in cursor.fetchall():
                result.append((
                    row['id'],
                    row['category'],
                    row['website'],
                    row['username'],
                    row['encrypted_password'],
                    row['notes'],
                    row['created_date']
                ))

            conn.close()
            print(f"Найдено паролей: {len(result)}")
            return result

        except Exception as e:
            print(f"Ошибка чтения паролей: {e}")
            return []

    def search_passwords(self, search_term):
        #Поиск паролей в базе данных
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT p.id, c.name as category, p.website, p.username, 
                       p.encrypted_password, p.notes, p.created_date
                FROM passwords p
                JOIN categories c ON p.category_id = c.id
                WHERE p.website LIKE ? OR p.username LIKE ? OR c.name LIKE ?
                ORDER BY p.website
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))

            result = []
            for row in cursor.fetchall():
                result.append((
                    row['id'],
                    row['category'],
                    row['website'],
                    row['username'],
                    row['encrypted_password'],
                    row['notes'],
                    row['created_date']
                ))

            conn.close()
            print(f"Поиск '{search_term}': найдено {len(result)} записей")
            return result

        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return []

    def delete_password(self, password_id):
        #Удалить пароль из базы данных
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM passwords WHERE id = ?', (password_id,))

            conn.commit()
            conn.close()

            print(f"Пароль ID {password_id} успешно удален")
            return True

        except Exception as e:
            print(f"Ошибка удаления пароля: {e}")
            return False

    def update_password(self, password_id, category_id, website, username, encrypted_password, notes):
        #Обновить пароль в базе данных
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE passwords 
                SET category_id = ?, website = ?, username = ?, encrypted_password = ?, notes = ?
                WHERE id = ?
            ''', (category_id, website, username, encrypted_password, notes, password_id))

            conn.commit()
            conn.close()

            print(f"Пароль ID {password_id} успешно обновлен")
            return True

        except Exception as e:
            print(f"Ошибка обновления пароля: {e}")
            return False