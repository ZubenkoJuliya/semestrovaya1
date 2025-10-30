import sqlite3
import os


def create_database():
    #Создание базы данных SQLite с тестовыми данными

    # Создаем папку если нет
    os.makedirs('database', exist_ok=True)

    # Подключаемся к базе данных (файл создастся автоматически)
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
            category_id INTEGER NOT NULL,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password TEXT NOT NULL,
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # Добавляем категории
    categories = [
        (1, 'Социальные сети', 'social'),
        (2, 'Электронная почта', 'email'),
        (3, 'Банки и финансы', 'bank'),
        (4, 'Работа', 'work'),
        (5, 'Игры', 'games'),
        (6, 'Образование', 'education'),
        (7, 'Здоровье', 'health'),
        (8, 'Покупки', 'shopping'),
        (9, 'Путешествия', 'travel'),
        (10, 'Еда', 'food')
    ]

    cursor.executemany(
        'INSERT OR IGNORE INTO categories (id, name, icon) VALUES (?, ?, ?)',
        categories
    )

    # Добавляем тестовые пароли
    passwords = [
        (1, 1, 'vk.com', 'petrov03_vk',
         'gAAAAABpAlUpSGA2zDGxT50YylbI9Gf0BgEdBr_0HPmyYD3ukKsfT_5d227Vh_ABjfy2XjVYk5_xWyMYBEWd5DFN9s2YibFIPjZE7uBNmfaulQ4kx52TNu4=',
         'Основная страница', '2025-10-29 22:58:00'),
        (2, 2, 'gmail.com', 'petrov030102@gmail.com',
         'gAAAAABpAlS8c7ph3wUeARkRVV1NdKgS8vTHdF932ZoP27FIOzgb1wUvoxYdgtp0GseSfCSbscrc2JT0W_4DbgtZzrrAUfqzwA==',
         'Рабочая почта', '2025-10-29 16:47:00'),
        (3, 3, 'sberbank.ru', 'petrov_sber',
         'gAAAAABpAjqvdQX9SIbCHpfkW4K3fOQ4VcJKUvSxQFECJJkudm2R3hcwlci_tZuTTGegqB-RQNTsHZizr9UB5G06NNv7wqsI9w==',
         'Основной счет', '2025-10-29 20:44:00'),
        (4, 4, 'company-portal', 'petrov_peter',
         'gAAAAABpAj9L4oBmfahD4PdzgwSfIldqAFGJAnNbs08Z0z1dEjoVMe_Jz9SCDn5x2UxMayzkiL9ziIJ6i3y7ImNr9rOaq_-V-FOKYAfcbo1wXeBwQkfwT3I=',
         'Внутренний портал', '2025-10-29 21:01:00'),
        (5, 1, 'ok.ru', 'PetyaPetrov',
         'gAAAAABpAkCThoavefh63gWornOsmE3MKvV-RhxcYY9x_V_cUGIYoHETYZWKYpfRmZpcX1S_tNuMfaRzaixBFJV0yHyq_yMc9qql15F87_f_-dpIT7IH2S0=',
         'Основная страница', '2025-10-29 23:28:03')
    ]

    cursor.executemany(
        'INSERT OR IGNORE INTO passwords (id, category_id, website, username, encrypted_password, notes, created_date) VALUES (?, ?, ?, ?, ?, ?, ?)',
        passwords
    )

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

    print("База данных успешно создана!")
    print("Файл: database/database.sqlite")
    print("Таблицы: categories, passwords")


if __name__ == "__main__":
    create_database()