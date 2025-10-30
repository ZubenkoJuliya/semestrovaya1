import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QInputDialog, QLineEdit
from main_window import MainWindow


def ask_master_password_before_app():
    # Запрос мастер-пароля до создания главного окна
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
    # Добавляем путь к иконкам и UI файлам для сборки
    if hasattr(sys, '_MEIPASS'):
        # Если запущено из собранного EXE
        os.chdir(sys._MEIPASS)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
