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


@app.route('/redis/keys')
def redis_keys():
    r = get_redis_connection()
    pattern = request.args.get('pattern', '*')
    keys = r.keys(pattern)
    return jsonify({'success': True, 'keys': keys})

@app.route('/redis/get/<key>')
def redis_get(key):
    r = get_redis_connection()
    value = r.get(key)
    return jsonify({
        'success': True,
        'key': key,
        'value': value,
        'type': 'string' if value else 'none'
    })

@app.route('/redis/hgetall/<key>')
def redis_hgetall(key):
    r = get_redis_connection()
    value = r.hgetall(key)
    return jsonify({
        'success': True,
        'key': key,
        'value': value,
        'type': 'hash' if value else 'none'
    })

@app.route('/redis/set', methods=['POST'])
def redis_set():
    data = request.json
    r = get_redis_connection()
    
    try:
        # Проверяем валидность JSON
        if data['type'] == 'string':
            json.loads(data['value'])  # Проверка на валидный JSON
            r.set(data['key'], data['value'])
            return jsonify({'success': True})
        elif data['type'] == 'hash':
            r.hset(data['key'], mapping=data['value'])
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/redis/delete/<key>', methods=['DELETE'])
def redis_delete(key):
    r = get_redis_connection()
    deleted = r.delete(key)
    return jsonify({'success': True, 'deleted': deleted})

@app.route('/redis-console')
def redis_console():
    return render_template('redis_console.html')


@app.route('/update_message', methods=['POST'])
def update_message():
    data = request.json
    user_id = data['user_id']
    message_id = int(data['message_id']) - 1  # Преобразуем в индекс
    new_content = data['new_content']
    
    r = get_redis_connection()
    key = f'fsm:{user_id}:{user_id}:data'
    data = r.get(key)
    
    if data:
        try:
            parsed = json.loads(data)
            if 'history' in parsed and message_id < len(parsed['history']):
                parsed['history'][message_id]['content'] = new_content
                r.set(key, json.dumps(parsed))
                return jsonify({'success': True})
        except json.JSONDecodeError:
            pass
    
    return jsonify({'success': False}), 400

@app.route('/delete_message', methods=['POST'])
def delete_message():
    data = request.json
    user_id = data['user_id']
    message_id = int(data['message_id']) - 1  # Преобразуем в индекс
    
    r = get_redis_connection()
    key = f'fsm:{user_id}:{user_id}:data'
    data = r.get(key)
    
    if data:
        try:
            parsed = json.loads(data)
            if 'history' in parsed and message_id < len(parsed['history']):
                del parsed['history'][message_id]
                r.set(key, json.dumps(parsed))
                return jsonify({'success': True})
        except json.JSONDecodeError:
            pass
    
    return jsonify({'success': False}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)