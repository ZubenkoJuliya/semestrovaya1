import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QInputDialog, QLineEdit


def ask_master_password_before_app():
    """Запрос мастер-пароля до создания главного окна"""
    app = QApplication([])

    password, ok = QInputDialog.getText(
        None,
        "Мастер-пароль",
        "Введите мастер-пароль для доступа к хранилищу:",
        QLineEdit.EchoMode.Password
    )

    if not ok:
        print("Ввод мастер-пароля отменен. Закрытие приложения.")
        sys.exit(0)

    if len(password) < 4:
        QMessageBox.critical(None, "Ошибка", "Мастер-пароль должен содержать минимум 4 символа")
        sys.exit(1)

    return password


def main():
    # Создаем необходимые папки
    os.makedirs('database', exist_ok=True)
    os.makedirs('icons', exist_ok=True)


    # Запрашиваем мастер-пароль ДО создания главного окна
    master_password = ask_master_password_before_app()

    # Создаем QApplication (если еще не создан)
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Password Vault")
    app.setApplicationVersion("1.0")

    # Устанавливаем стиль приложения
    app.setStyle('Fusion')

    # Импортируем и создаем главное окно
    from main_window import MainWindow
    window = MainWindow(master_password)  # Передаем пароль в конструктор
    window.show()

    # Запускаем приложение
    sys.exit(app.exec())


if __name__ == '__main__':
    main()