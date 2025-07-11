from flask import Flask, render_template, request, url_for, redirect, jsonify
import redis
import json
import time
from datetime import datetime


app = Flask(__name__, static_folder='static')

# Конфигурация Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

def add_message_to_history(user_id, role, content):
    r = get_redis_connection()
    key = f'fsm:{user_id}:{user_id}:data'
    
    # Получаем текущие данные
    data = r.get(key)
    if data:
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            parsed = {'history': []}
    else:
        parsed = {'history': []}
    
    # Добавляем новое сообщение
    new_message = {
        'role': role,
        'content': content,
        'timestamp': int(time.time())  # Добавляем временную метку
    }
    parsed['history'].append(new_message)
    
    # Сохраняем обновленные данные
    r.set(key, json.dumps(parsed))
    return True

def delete_user_dialog(user_id):
    r = get_redis_connection()
    key = f'fsm:{user_id}:{user_id}:data'
    return r.delete(key)


def get_redis_connection():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )

def get_available_users():
    r = get_redis_connection()
    keys = r.keys('fsm:*:data')
    return sorted(list(set(key.split(':')[1] for key in keys)))

def get_user_history(user_id):
    r = get_redis_connection()
    key = f'fsm:{user_id}:{user_id}:data'
    data = r.get(key)
    
    if not data:
        return []
    
    try:
        parsed = json.loads(data)
        return parsed.get('history', [])
    except json.JSONDecodeError:
        return []

@app.route('/')
def index():
    users = get_available_users()
    return render_template('index.html', users=users)

@app.route('/api/history/<user_id>')
def api_history(user_id):
    history = get_user_history(user_id)
    return jsonify(history)

@app.route('/history')
def show_history():
    user_id = request.args.get('user_id')
    history = get_user_history(user_id)
    return render_template('history.html', 
                         user_id=user_id,
                         history=history)

@app.route('/delete_dialog')
def delete_dialog():
    user_id = request.args.get('user_id')
    if not user_id:
        return "User ID is required", 400
    
    deleted = delete_user_dialog(user_id)
    if deleted:
        return redirect(url_for('index'))
    else:
        return "Dialog not found", 404
    
@app.route('/send_message', methods=['POST'])
def send_message():
    user_id = request.form.get('user_id')
    role = request.form.get('role')
    content = request.form.get('content')
    
    if not all([user_id, role, content]):
        return "Missing required parameters", 400
    
    if role not in ['user', 'bot']:
        return "Invalid role", 400
    
    if add_message_to_history(user_id, role, content):
        return redirect(url_for('show_history', user_id=user_id))
    else:
        return "Failed to send message", 500

@app.template_filter('datetime')
def format_datetime(timestamp):
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)