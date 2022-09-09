import sqlite3
import secrets

from flask_restful import reqparse, abort

_DB_FILE = 'auth.db'
_TOKEN_LEN_BYTE = 16

_connection = sqlite3.connect(_DB_FILE)
_cursor = _connection.cursor()

#_cursor.execute("DROP TABLE users")
# Generate Users Table
_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    token TEXT PRIMARY KEY,
    is_admin INT NOT NULL,
    expire_type INT NOT NULL,
    expire_date DATE,
    expire_number INT
);
""")

_connection.commit()


def _insert_user(token, is_admin, expire_type, expire_date, expire_number):
    connection = sqlite3.connect(_DB_FILE)
    cursor = connection.cursor()

    # Generate Users Table
    cursor.execute(f"""
    INSERT INTO users('token', 'is_admin', 'expire_type', 'expire_date', 'expire_number') 
    VALUES(?,?,?,?,?); 
    """, (token, is_admin, expire_type, expire_date, expire_number))

    connection.commit()


def generate_user(is_admin):
    connection = sqlite3.connect(_DB_FILE)
    cursor = connection.cursor()

    token = secrets.token_hex(_TOKEN_LEN_BYTE)
    if cursor.execute("SELECT * FROM USERS WHERE token = ?", (token,)).fetchone() is None:
        _insert_user(token, int(is_admin), 0, None, None)
        connection.commit()
        return token
    else:
        connection.commit()
        print("Token already in use, regenerating")
        generate_user(is_admin)


def auth_normal_user(token):
    if not auth_expire(token):
        return False

    connection = sqlite3.connect(_DB_FILE)
    cursor = connection.cursor()

    user = cursor.execute("SELECT * FROM users WHERE token = ?", (token,)).fetchone()

    return user is not None


def auth_admin_user(token):
    if not auth_expire(token):
        return False

    connection = sqlite3.connect(_DB_FILE)
    cursor = connection.cursor()

    user = cursor.execute("SELECT * FROM users WHERE token = ? AND is_admin = 1", (token,)).fetchone()

    return user is not None


def auth_expire(token):
    connection = sqlite3.connect(_DB_FILE)
    cursor = connection.cursor()

    user = cursor.execute("SELECT * FROM users WHERE token = ?", (token,)).fetchone()
    connection.commit()

    if not user:
        return False

    mode = user[2]

    if mode == 0:
        return True

    return False


def auth_default():
    parser = reqparse.RequestParser()
    parser.add_argument('token', location='headers')
    args = parser.parse_args()

    if not auth_normal_user(args['token']):
        abort(401, message='Invalid or nonexistent token')


def auth_admin():
    auth_default()

    parser = reqparse.RequestParser()
    parser.add_argument('token', location='headers')
    args = parser.parse_args()

    if not auth_admin_user(args['token']):
        abort(401, message='Invalid authorization')
