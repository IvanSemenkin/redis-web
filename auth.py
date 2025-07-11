from flask import Flask
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'ваш_секретный_ключ'  # Замените на реальный секретный ключ

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модель пользователя
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Пример "базы данных" пользователей
users = {
    1: User(1, 'admin', generate_password_hash('admin123')),
    2: User(2, 'user', generate_password_hash('user123'))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))