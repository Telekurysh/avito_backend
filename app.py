from flask import Flask, request, jsonify, render_template, redirect, url_for
import psycopg2
from psycopg2 import sql
from flask_caching import Cache
from api import api

app = Flask(__name__)
api.init_app(app)

cache = Cache()
app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    dbname='avito',
    user='mihailmamaev',
    password='qwerty',
    host='localhost'
)
cur = conn.cursor()


def check_token_and_role(token):
    cur.execute("SELECT role FROM users WHERE token = %s", (token,))
    user_role = cur.fetchone()
    if user_role:
        return user_role[0]
    else:
        return None


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
        user_id = cur.fetchone()
        if user_id:
            user_id = user_id[0]
        cur.execute("SELECT token from users WHERE id = %s", (user_id,))
        token = cur.fetchone()[0]
        if user_id:
            # Авторизация успешна, устанавливаем сессию или токен
            return redirect(url_for('home', token=token))
        else:
            # Авторизация неудачна
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'user'
        token = 'user'
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            return render_template('register.html', error='Username already exists')
        else:
            cur.execute("INSERT INTO users (username, password, role, token) VALUES (%s, %s, %s, %s)",
                        (username, password, role, token))
            conn.commit()
            # Пользователь успешно зарегистрирован, можно перенаправить на страницу входа
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/home')
def home():
    token = request.args.get('token')
    return render_template('home.html', token=token)


# Метод получения баннера для пользователя
@app.route('/user_banner', methods=['GET'])
def get_user_banner(*args):
    if args[0]:
        token = args[0]
    else:
        token = request.args.get('token')
    tag_id = request.args.get('tag_id')
    feature_id = request.args.get('feature_id')
    use_last_revision = request.args.get('use_last_revision', False)
    tag_id = 1
    feature_id = 1
    if not token:
        return jsonify({"error": "Missing token"}), 401
    user_role = check_token_and_role(token)
    if not user_role:
        return jsonify({"error": "Invalid token"}), 401

    # Запрос к базе данных для получения баннера
    cur.execute("""
        SELECT b.content
        FROM banners b
        JOIN banner_tags bt ON b.id = bt.banner_id
        WHERE bt.tag_id = (%s)
        AND b.feature_id = %s
        AND b.is_active = TRUE
        ORDER BY b.updated_at DESC
        LIMIT 1;
    """, (tag_id, feature_id))
    banner = cur.fetchone()
    print(banner)
    if banner:
        return jsonify(banner[0])
    else:
        return jsonify({"error": "Banner not found"}), 404


# Метод получения всех баннеров с фильтрацией
@app.route('/banner', methods=['GET'])
def get_banners(*args):
    if args[0]:
        token = args[0]
    else:
        token = request.args.get('token')
    feature_id = request.args.get('feature_id')
    tag_id = request.args.get('tag_id')
    limit = request.args.get('limit', 10)
    offset = request.args.get('offset', 0)

    user_role = check_token_and_role(token)
    if user_role is None:
        return jsonify({"error": "Invalid token"}), 401
    elif user_role != 'admin':
        return jsonify({"error": "Permission denied"}), 403

    # Запрос к базе данных для получения всех баннеров с фильтрацией
    query = """
        SELECT b.id as banner_id, array_agg(bt.tag_id) as tag_ids, b.feature_id, 
               b.content, b.is_active, b.created_at, b.updated_at
        FROM banners b
        JOIN banner_tags bt ON b.id = bt.banner_id
        WHERE 1=1
    """
    params = []

    if feature_id:
        query += " AND b.feature_id = %s"
        params.append(feature_id)
    if tag_id:
        query += " AND bt.tag_id = %s"
        params.append(tag_id)

    query += " GROUP BY b.id"

    cur.execute(query, params)
    banners = cur.fetchall()

    result = []
    for banner in banners:
        result.append({
            "banner_id": banner[0],
            "tag_ids": banner[1],
            "feature_id": banner[2],
            "content": banner[3],
            "is_active": banner[4],
            "created_at": banner[5],
            "updated_at": banner[6]
        })

    return jsonify(result)


@app.route('/banner', methods=['GET'])
def get_banners_with_filter(id, *args):
    if args[0]:
        token = args[0]
    else:
        token = request.args.get('token')
    feature_id = request.args.get('feature_id')
    tag_id = request.args.get('tag_id')

    # Проверка авторизации
    user_role = check_token_and_role(token)
    if user_role is None:
        return jsonify({"error": "Invalid token"}), 401

    # Запрос к базе данных для получения всех баннеров с фильтрацией
    query = """
        SELECT b.id as banner_id, array_agg(bt.tag_id) as tag_ids, b.feature_id, 
               b.content, b.is_active, b.created_at, b.updated_at
        FROM banners b
        JOIN banner_tags bt ON b.id = bt.banner_id
        WHERE 1=1
    """
    params = []

    if feature_id:
        query += " AND b.feature_id = %s"
        params.append(feature_id)
    if tag_id:
        query += " AND bt.tag_id = %s"
        params.append(tag_id)

    query += " GROUP BY b.id"

    cur.execute(query, params)
    banners = cur.fetchall()

    result = []
    for banner in banners:
        result.append({
            "banner_id": banner[0],
            "tag_ids": banner[1],
            "feature_id": banner[2],
            "content": banner[3],
            "is_active": banner[4],
            "created_at": banner[5],
            "updated_at": banner[6]
        })

    return jsonify(result)


# Метод создания нового баннера
@app.route('/banner/', methods=['POST'])
def create_banner(*args):
    if args[0]:
        token = args[0]
    else:
        token = request.args.get('token')
    data = request.get_json()

    user_role = check_token_and_role(token)
    if user_role is None:
        return jsonify({"error": "Invalid token"}), 401
    elif user_role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    # Вставка нового баннера в базу данных
    cur.execute("""
        INSERT INTO banners (feature_id, content, is_active)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (data['feature_id'], data['content'], data.get('is_active', True)))
    banner_id = cur.fetchone()[0]

    # Вставка связей тегов с баннером в базу данных
    for tag_id in data['tag_ids']:
        cur.execute("""
            INSERT INTO banner_tags (banner_id, tag_id)
            VALUES (%s, %s)
        """, (banner_id, tag_id))

    conn.commit()

    return jsonify({"banner_id": banner_id}), 201


# Метод обновления баннера
@app.route('/banner/<int:id>', methods=['PATCH'])
def update_banner(id, *args):
    if args[0]:
        token = args[0]
    else:
        token = request.args.get('token')
    data = request.get_json()

    user_role = check_token_and_role(token)
    if user_role is None:
        return jsonify({"error": "Invalid token"}), 401
    elif user_role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    # Обновление содержимого баннера
    update_fields = []
    if 'tag_ids' in data:
        # Удаление старых связей с тегами
        cur.execute("DELETE FROM banner_tags WHERE banner_id = %s", (id,))
        # Вставка новых связей с тегами
        for tag_id in data['tag_ids']:
            cur.execute("INSERT INTO banner_tags (banner_id, tag_id) VALUES (%s, %s)", (id, tag_id))
    if 'feature_id' in data:
        update_fields.append("feature_id = %s")
    if 'content' in data:
        update_fields.append("content = %s")
    if 'is_active' in data:
        update_fields.append("is_active = %s")

    if update_fields:
        query = "UPDATE banners SET " + ", ".join(update_fields) + ", updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        cur.execute(query, (*[data[field] for field in update_fields], id))
        conn.commit()

    return '', 200


# Метод удаления баннера
@app.route('/banner/<int:id>', methods=['DELETE'])
def delete_banner(id, *args):
    if args[0]:
        token = args[0]
    else:
        token = request.args.get('token')
    user_role = check_token_and_role(token)
    if user_role is None:
        return jsonify({"error": "Invalid token"}), 401
    elif user_role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    # Удаление баннера из базы данных
    cur.execute("DELETE FROM banners WHERE id = %s", (id,))
    conn.commit()

    return '', 204


if __name__ == '__main__':
    app.run(debug=True)
