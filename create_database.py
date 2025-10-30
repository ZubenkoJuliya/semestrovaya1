import sqlite3
import os


def create_database():
    # Создание базы данных и таблиц
    # Создаем папку database если её нет
    os.makedirs('database', exist_ok=True)

    conn = sqlite3.connect('database/database.sqlite')
    cursor = conn.cursor()

    # Создаем таблицу категорий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            icon TEXT NOT NULL
        )
    ''')

    # Создаем таблицу паролей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password TEXT NOT NULL,
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # Добавляем стандартные категории
    categories = [
        ('Соцсети', 'social'),
        ('Почта', 'email'),
        ('Банки', 'bank'),
        ('Работа', 'work'),
        ('Игры', 'games'),
        ('Образование', 'education'),
        ('Здоровье', 'health'),
        ('Покупки', 'shopping'),
        ('Путешествия', 'travel'),
        ('Еда', 'food')
    ]

    cursor.executemany(
        'INSERT OR IGNORE INTO categories (name, icon) VALUES (?, ?)',
        categories
    )

    conn.commit()
    conn.close()
    print("✅ База данных создана ")


if __name__ == "__main__":
    create_database()
