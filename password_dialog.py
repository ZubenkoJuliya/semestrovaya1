from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QMessageBox, QLineEdit
from PyQt6.QtGui import QFont, QIcon
import os


class PasswordDialog(QDialog):
    def __init__(self, db, security, categories, parent=None, password_data=None):
        super().__init__(parent)
        uic.loadUi('password_dialog.ui', self)

        self.db = db
        self.security = security
        self.categories = categories
        self.password_data = password_data  # Данные для редактирования
        self.is_editing = password_data is not None

        print("Создан диалог пароля")
        self.setup_ui()
        self.setup_category_icons()  # Добавляем иконки для категорий

    def get_icon_for_category(self, icon_name):
        #Получить картинку для категории по имени иконки
        # Соответствие имен иконок из базы данных и файлов картинок
        icon_files = {
            'social': 'social.png',
            'email': 'email.png',
            'bank': 'bank.png',
            'work': 'work.png',
            'games': 'games.png',
            'education': 'education.png',
            'health': 'health.png',
            'shopping': 'shopping.png',
            'travel': 'travel.png',
            'food': 'food.png'
        }

        # Получаем имя файла для категории
        filename = icon_files.get(icon_name, 'default.png')
        icon_path = f'icons/{filename}'

        # Если файл существует - используем его
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            # Fallback - простая текстовая иконка
            print(f"Файл иконки не найден: {icon_path}")
            return QIcon()  # Пустая иконка

    def setup_category_icons(self):
        #Добавление картинок для категорий в комбобокс
        self.category_combo.clear()

        for category_id, name, icon in self.categories:
            category_icon = self.get_icon_for_category(icon)
            self.category_combo.addItem(category_icon, name, category_id)

        print(f"Загружено категорий в диалог: {self.category_combo.count()}")

    def setup_ui(self):
        #Настройка интерфейса
        # Настраиваем поле пароля
        font = QFont()
        font.setFamily("Courier New")
        self.password_input.setFont(font)

        # Подключаем сигналы
        self.show_password_check.stateChanged.connect(self.toggle_password_visibility)
        self.generate_btn.clicked.connect(self.open_generator)
        self.save_btn.clicked.connect(self.save_password)
        self.cancel_btn.clicked.connect(self.reject)

        # Если редактирование, заполняем поля
        if self.is_editing:
            self.fill_form_data()
            self.setWindowTitle("Редактировать пароль")
        else:
            self.setWindowTitle("Добавить пароль")

        print("Интерфейс диалога пароля настроен")

    def toggle_password_visibility(self):
        #Переключение видимости пароля
        if self.show_password_check.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def fill_form_data(self):
        #Заполнение формы данными для редактирования
        if not self.password_data:
            return

        password_id, category_name, website, username, encrypted_password, notes, created_date = self.password_data

        # Находим индекс категории
        category_index = -1
        for i in range(self.category_combo.count()):
            if self.category_combo.itemText(i) == category_name:
                category_index = i
                break

        if category_index >= 0:
            self.category_combo.setCurrentIndex(category_index)

        self.website_input.setText(website)
        self.username_input.setText(username)

        # Расшифровываем пароль
        try:
            decrypted_password = self.security.decrypt_password(encrypted_password)
            self.password_input.setText(decrypted_password)
        except Exception as e:
            print(f"Ошибка расшифровки пароля: {e}")
            self.password_input.setText("")

        self.notes_input.setPlainText(notes if notes else "")

        print(f"Форма заполнена данными для редактирования: {website}")

    def open_generator(self):
        #Открытие генератора паролей
        try:
            from generator_dialog import GeneratorDialog
            dialog = GeneratorDialog(self)
            if dialog.exec():
                generated_password = dialog.get_generated_password()
                if generated_password:
                    self.password_input.setText(generated_password)
                    print("Пароль из генератора установлен в поле")
        except Exception as e:
            print(f"Ошибка открытия генератора: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть генератор паролей")

    def save_password(self):
        # Сохранение пароля
        try:
            # Получаем данные из формы
            category_index = self.category_combo.currentIndex()
            if category_index < 0:
                QMessageBox.warning(self, "Ошибка", "Выберите категорию")
                return

            category_id = self.category_combo.itemData(category_index)
            website = self.website_input.text().strip()
            username = self.username_input.text().strip()
            password = self.password_input.text()  # Убедитесь, что это строка!
            notes = self.notes_input.toPlainText().strip()

            # Валидация
            if not website:
                QMessageBox.warning(self, "Ошибка", "Введите название сайта")
                self.website_input.setFocus()
                return

            if not username:
                QMessageBox.warning(self, "Ошибка", "Введите логин/имя пользователя")
                self.username_input.setFocus()
                return

            if not password:
                QMessageBox.warning(self, "Ошибка", "Введите пароль")
                self.password_input.setFocus()
                return

            print(f"Тип password: {type(password)}, Значение: {password}")

            if isinstance(password, tuple):
                # Если password оказался кортежем, берем первый элемент (предположительно пароль)
                password = password[0] if password else ""
                print(f"Исправлен password: {password}")

            # Шифруем пароль
            encrypted_password = self.security.encrypt_password(password)

            # Сохраняем в базу
            if self.is_editing:
                success = self.db.update_password(
                    self.password_data[0], category_id, website, username,
                    encrypted_password, notes
                )
                action = "обновлен"
            else:
                success = self.db.add_password(
                    category_id, website, username, encrypted_password, notes
                )
                action = "добавлен"

            if success:
                print(f"Пароль успешно {action}: {website}")
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить пароль")

        except Exception as e:
            print(f"Ошибка сохранения пароля: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")