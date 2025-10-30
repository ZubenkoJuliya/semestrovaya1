import secrets
import string
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class SecurityManager:
    def __init__(self, master_password):
        self.master_password = master_password
        self.fernet = self._create_fernet_key(master_password)

    def _create_fernet_key(self, password):
        #Создание ключа шифрования из мастер-пароля с фиксированной солью
        password_bytes = password.encode()

        # Фиксированная соль для всего приложения
        salt = b'my_password_manager_salt_2024'

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return Fernet(key)

    def encrypt_password(self, password):
        #Шифрование пароля
        try:
            encrypted = self.fernet.encrypt(password.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"Ошибка шифрования: {e}")
            return ""

    def decrypt_password(self, encrypted_password):
        #Дешифрование пароля
        try:
            decrypted = self.fernet.decrypt(encrypted_password.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"Ошибка дешифрования: {e}")
            return ""

    def check_password_strength(self, password):
        #Проверка надежности пароля
        score = 0
        if len(password) >= 8:
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?`~' for c in password):
            score += 1

        return min(score * 20, 100)

    def generate_password(self, length=12, use_uppercase=True, use_lowercase=True,
                          use_digits=True, use_symbols=True):
        #Генерация случайного пароля
        characters = ""
        if use_lowercase:
            characters += string.ascii_lowercase
        if use_uppercase:
            characters += string.ascii_uppercase
        if use_digits:
            characters += string.digits
        if use_symbols:
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?`~"

        if not characters:
            characters = string.ascii_letters + string.digits

        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password


class PasswordGenerator:
    @staticmethod
    def generate(length=12, uppercase=True, lowercase=True, digits=True, symbols=True):
        #Статический метод для генерации паролей
        security = SecurityManager("temp")
        return security.generate_password(length, uppercase, lowercase, digits, symbols)

    @staticmethod
    def check_strength(password):
        #Статический метод для проверки надежности
        security = SecurityManager("temp")
        return security.check_password_strength(password)