import sys
import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QInputDialog, QLineEdit, QHeaderView, \
    QAbstractItemView
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from database import SQLiteDatabase


class MainWindow(QMainWindow):
    def __init__(self, master_password=None):
        super().__init__()

        self.db = SQLiteDatabase()
        self.security = None
        self.current_passwords = []
        self.all_passwords = []
        self.master_password = master_password

        uic.loadUi('main_window.ui', self)

        print("Инициализация главного окна...")
        self.setup_ui()
        self.setup_shortcuts()
        self.ask_master_password()

    def get_icon_for_category(self, icon_name):
        #Получить картинку для категории по имени иконки
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

    def setup_ui(self):
        #Настройка интерфейса
        # Подключаем сигналы
        self.search_input.returnPressed.connect(self.search_passwords)
        self.category_filter.currentIndexChanged.connect(self.filter_by_category)
        self.search_btn.clicked.connect(self.search_passwords)
        self.clear_filters_btn.clicked.connect(self.clear_filters)

        self.add_btn.clicked.connect(self.add_password)
        self.edit_btn.clicked.connect(self.edit_password)
        self.delete_btn.clicked.connect(self.delete_password)
        self.generate_btn.clicked.connect(self.open_generator)
        self.refresh_btn.clicked.connect(self.refresh_passwords)

        # Настраиваем таблицу
        self.passwords_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.passwords_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.passwords_table.doubleClicked.connect(self.edit_password)

        # Настройка заголовков таблицы
        header = self.passwords_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Сайт
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Логин

        # Статус
        self.statusBar().showMessage("Готово")
        print("Интерфейс настроен")

    def setup_shortcuts(self):
        #Настройка горячих клавиш
        # Ctrl+N - новая запись
        self.add_action = QAction("Добавить", self)
        self.add_action.setShortcut(QKeySequence.StandardKey.New)
        self.add_action.triggered.connect(self.add_password)
        self.addAction(self.add_action)

        # Delete - удалить запись
        self.delete_action = QAction("Удалить", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.triggered.connect(self.delete_password)
        self.addAction(self.delete_action)

        # F5 - обновить
        self.refresh_action = QAction("Обновить", self)
        self.refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        self.refresh_action.triggered.connect(self.refresh_passwords)
        self.addAction(self.refresh_action)

        # Ctrl+F - поиск
        self.search_action = QAction("Поиск", self)
        self.search_action.setShortcut(QKeySequence.StandardKey.Find)
        self.search_action.triggered.connect(self.focus_search)
        self.addAction(self.search_action)

    def ask_master_password(self):
        #Запрос мастер-пароля
        from security import SecurityManager

        if self.master_password:
            password = self.master_password
        else:
            password, ok = QInputDialog.getText(
                self, "Мастер-пароль", "Введите мастер-пароль:",
                QLineEdit.EchoMode.Password
            )
            if not ok:
                sys.exit(0)

        if len(password) < 4:
            QMessageBox.warning(self, "Ошибка", "Минимум 4 символа")
            sys.exit(1)

        self.security = SecurityManager(password)
        self.load_categories()
        self.refresh_passwords()

    def load_categories(self):
        #Загрузка категорий в комбобокс с картинками
        self.category_filter.clear()

        # Добавляем "Все категории" без иконки
        self.category_filter.addItem("Все категории", None)

        categories = self.db.get_categories()
        for category_id, name, icon in categories:
            # Создаем картинку для категории
            category_icon = self.get_icon_for_category(icon)
            self.category_filter.addItem(category_icon, name, category_id)

        print(f"Загружено категорий в фильтр: {self.category_filter.count()}")

    def refresh_passwords(self):
        #Обновление списка паролей
        try:
            self.all_passwords = self.db.get_all_passwords()
            self.apply_filters()
            self.statusBar().showMessage(f"Загружено записей: {len(self.all_passwords)}")
        except Exception as e:
            print(f"Ошибка при обновлении паролей: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить пароли: {str(e)}")

    def apply_filters(self):
        #Применение всех активных фильтров
        from PyQt6.QtGui import QStandardItemModel, QStandardItem

        filtered_passwords = self.all_passwords.copy()

        # Фильтрация по категории
        selected_category_id = self.category_filter.currentData()
        if selected_category_id is not None:
            filtered_passwords = [pwd for pwd in filtered_passwords if pwd[1] == self.category_filter.currentText()]
            print(f"Фильтр по категории: {self.category_filter.currentText()}")

        # Фильтрация по поисковому запросу
        search_term = self.search_input.text().strip()
        if search_term:
            search_term = search_term.lower()
            filtered_passwords = [pwd for pwd in filtered_passwords
                                  if (search_term in pwd[2].lower() or  # website
                                      search_term in pwd[3].lower() or  # username
                                      search_term in pwd[1].lower())]  # category name
            print(f"Фильтр по поиску: '{search_term}'")

        # Отображаем отфильтрованные данные
        self.current_passwords = filtered_passwords

        # Создаем модель таблицы
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['ID', 'Категория', 'Сайт', 'Логин', 'Пароль', 'Заметки', 'Дата создания'])

        for pwd in filtered_passwords:
            password_id, category, website, username, encrypted_password, notes, created_date = pwd

            masked_password = "••••••••"
            display_notes = notes[:50] + "..." if notes and len(notes) > 50 else (notes or "")

            row_items = [
                QStandardItem(str(password_id)),
                QStandardItem(category),
                QStandardItem(website),
                QStandardItem(username),
                QStandardItem(masked_password),
                QStandardItem(display_notes),
                QStandardItem(str(created_date))
            ]
            model.appendRow(row_items)

        self.passwords_table.setModel(model)
        self.passwords_table.setColumnHidden(0, True)

        self.statusBar().showMessage(f"Показано записей: {len(filtered_passwords)} (всего: {len(self.all_passwords)})")
        print(f"Отображено паролей в таблице: {len(filtered_passwords)}")

    def filter_by_category(self):
        #Фильтрация по выбранной категории
        print("Фильтрация по категории...")
        self.apply_filters()

    def search_passwords(self):
        #Поиск паролей
        search_term = self.search_input.text().strip()
        print(f"Выполнение поиска: '{search_term}'")
        self.apply_filters()

    def clear_filters(self):
        #Сброс всех фильтров
        print("Сброс фильтров")
        self.search_input.clear()
        self.category_filter.setCurrentIndex(0)
        self.apply_filters()

    def add_password(self):
        #Добавление нового пароля
        print("Нажата кнопка 'Добавить пароль'")
        try:
            from password_dialog import PasswordDialog

            categories = self.db.get_categories()
            dialog = PasswordDialog(self.db, self.security, categories, self)
            if dialog.exec():
                self.refresh_passwords()
                self.statusBar().showMessage("Пароль успешно добавлен")
        except Exception as e:
            print(f"Ошибка в add_password: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог добавления: {str(e)}")

    def edit_password(self):
        #Редактирование выбранного пароля
        print("Нажата кнопка 'Редактировать'")
        try:
            from password_dialog import PasswordDialog

            selected_indexes = self.passwords_table.selectionModel().selectedRows()
            if not selected_indexes:
                QMessageBox.information(self, "Информация", "Выберите пароль для редактирования")
                return

            selected_row = selected_indexes[0].row()
            if not self.current_passwords or selected_row >= len(self.current_passwords):
                QMessageBox.warning(self, "Ошибка", "Неверный выбор пароля")
                return

            password_data = self.current_passwords[selected_row]
            categories = self.db.get_categories()
            dialog = PasswordDialog(self.db, self.security, categories, self, password_data)
            if dialog.exec():
                self.refresh_passwords()
                self.statusBar().showMessage("Пароль успешно обновлен")
        except Exception as e:
            print(f"Ошибка в edit_password: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог редактирования: {str(e)}")

    def delete_password(self):
        #Удаление выбранного пароля
        print("Нажата кнопка 'Удалить'")
        try:
            selected_indexes = self.passwords_table.selectionModel().selectedRows()
            if not selected_indexes:
                QMessageBox.information(self, "Информация", "Выберите пароль для удаления")
                return

            selected_row = selected_indexes[0].row()
            if not self.current_passwords or selected_row >= len(self.current_passwords):
                QMessageBox.warning(self, "Ошибка", "Неверный выбор пароль")
                return

            password_data = self.current_passwords[selected_row]
            password_id = password_data[0]
            website = password_data[2]

            reply = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить пароль для {website}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                success = self.db.delete_password(password_id)
                if success:
                    self.refresh_passwords()
                    self.statusBar().showMessage("Пароль успешно удален")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить пароль")
        except Exception as e:
            print(f"Ошибка в delete_password: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить пароль: {str(e)}")

    def open_generator(self):
        #Открытие генератора паролей
        print("Нажата кнопка 'Генератор паролей'")
        try:
            from generator_dialog import GeneratorDialog
            dialog = GeneratorDialog(self)
            dialog.exec()
        except Exception as e:
            print(f"Ошибка в open_generator: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть генератор: {str(e)}")

    def focus_search(self):
        #Фокус на поле поиска
        self.search_input.setFocus()
        self.search_input.selectAll()