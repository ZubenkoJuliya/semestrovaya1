from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt6.QtGui import QFont
import pyperclip
from security import PasswordGenerator


class GeneratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('generator_dialog.ui', self)

        print("Создан диалог генератора паролей")
        self.setup_ui()
        self.generate_password()

    def setup_ui(self):
        #Настройка интерфейса после загрузки из .ui файла

        # Настраиваем поле для пароля
        font = QFont()
        font.setPointSize(12)
        font.setFamily("Courier New")
        self.password_output.setFont(font)
        self.password_output.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")

        # Подключаем сигналы
        self.generate_btn.clicked.connect(self.generate_password)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.length_slider.valueChanged.connect(self.update_length_label)

        self.uppercase_check.stateChanged.connect(self.generate_password)
        self.lowercase_check.stateChanged.connect(self.generate_password)
        self.digits_check.stateChanged.connect(self.generate_password)
        self.symbols_check.stateChanged.connect(self.generate_password)

        print("Интерфейс генератора настроен")

    def update_length_label(self, value):
        #Обновление метки длины пароля
        self.length_label.setText(f"Длина пароля: {value}")
        self.generate_password()

    def generate_password(self):
        #Генерация нового пароля
        length = self.length_slider.value()
        uppercase = self.uppercase_check.isChecked()
        lowercase = self.lowercase_check.isChecked()
        digits = self.digits_check.isChecked()
        symbols = self.symbols_check.isChecked()

        print(
            f"Генерация пароля: длина={length}, uppercase={uppercase}, lowercase={lowercase}, digits={digits}, symbols={symbols}")

        # Проверяем, что выбрана хотя бы одна опция
        if not any([uppercase, lowercase, digits, symbols]):
            self.password_output.setText("Выберите хотя бы один тип символов")
            self.strength_label.setText("")
            return

        password = PasswordGenerator.generate(length, uppercase, lowercase, digits, symbols)
        self.password_output.setText(password)

        # Показываем надежность пароля
        strength = PasswordGenerator.check_strength(password)
        if strength < 40:
            strength_text = "Слабый пароль"
            color = "red"
        elif strength < 70:
            strength_text = "Средний пароль"
            color = "orange"
        else:
            strength_text = "Сильный пароль"
            color = "green"

        self.strength_label.setText(f"Надежность: {strength_text} ({strength}%)")
        self.strength_label.setStyleSheet(f"color: {color}; font-weight: bold;")

        print(f"Пароль сгенерирован, надежность: {strength}%")

    def copy_to_clipboard(self):
        #Копирование пароля в буфер обмена
        password = self.password_output.text()
        if password and password != "Выберите хотя бы один тип символов":
            pyperclip.copy(password)
            original_text = self.copy_btn.text()
            self.copy_btn.setText("Скопировано!")
            self.copy_btn.setStyleSheet("background-color: green; color: white;")

            # Возвращаем исходный текст через 2 секунды
            QApplication.processEvents()
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.reset_copy_button(original_text))

            print("Пароль скопирован в буфер обмена")
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала сгенерируйте пароль")

    def reset_copy_button(self, original_text):
        #Восстановление исходного текста кнопки
        self.copy_btn.setText(original_text)
        self.copy_btn.setStyleSheet("")

    def get_generated_password(self):
        #Получение сгенерированного пароля
        password = self.password_output.text()
        if password and password != "Выберите хотя бы один тип символов":
            return password
        return ""
