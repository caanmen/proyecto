from flask_cors import CORS
from flask import Flask, request, jsonify, make_response
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'tu_super_secreto'
CORS(app, resources={r"/*": {"origins": "*"}})  # Permitir solicitudes desde cualquier origen

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def get_connection(self):
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(
                dbname="rest",
                user="postgres",
                password="adm",
                host="localhost"
            )
        return self.connection

def get_db_connection():
    return DatabaseConnection().get_connection()

class ResponseFactory:
    @staticmethod
    def create_response(response_type, message, data=None):
        if response_type == 'success':
            return jsonify({'status': 'success', 'message': message, 'data': data}), 200
        elif response_type == 'error':
            return jsonify({'status': 'error', 'message': message}), 400
        elif response_type == 'not_found':
            return jsonify({'status': 'not_found', 'message': message}), 404

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response

def _corsify_actual_response(response):
    if isinstance(response, tuple):
        response, status = response
        response = make_response(response, status)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/')
def home():
    return 'Bienvenido a la API de ReservaFacil!'

@app.route('/create_user', methods=['POST', 'OPTIONS'])
def create_user():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    user_details = request.json
    nombre = user_details['nombre']
    apellido = user_details['apellido']
    correo = user_details['correo']
    telefono = user_details['telefono']
    tipo_usuario = user_details['tipo_usuario']
    contrasena = user_details['contrasena']

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO public.usuarios (nombre, apellido, correo, telefono, tipo_usuario, contrasena) VALUES (%s, %s, %s, %s, %s, %s)',
            (nombre, apellido, correo, telefono, tipo_usuario, contrasena)
        )
        conn.commit()
        response = ResponseFactory.create_response('success', 'Usuario creado exitosamente')
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    credentials = request.json
    correo = credentials['correo']
    contrasena = credentials['contrasena']

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(
            'SELECT * FROM public.usuarios WHERE correo = %s AND contrasena = %s',
            (correo, contrasena)
        )
        user = cursor.fetchone()
        if user:
            additional_claims = {"tipo_usuario": user['tipo_usuario']}
            response = ResponseFactory.create_response('success', 'Login exitoso', {'user': user['correo'], 'tipo_usuario': additional_claims})
            return _corsify_actual_response(response)
        else:
            response = ResponseFactory.create_response('error', 'Credenciales inválidas')
            return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/users', methods=['GET', 'OPTIONS'])
def get_users():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT id, nombre, apellido FROM public.usuarios")
        users = cursor.fetchall()
        response = ResponseFactory.create_response('success', 'Usuarios obtenidos con éxito', users)
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

@app.route('/user/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_user(user_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM public.usuarios WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            response = ResponseFactory.create_response('not_found', 'Usuario no encontrado')
            return _corsify_actual_response(response)
        response = ResponseFactory.create_response('success', 'Usuario encontrado', user)
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

@app.route('/user/<int:user_id>', methods=['PUT', 'OPTIONS'])
def update_user(user_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    user_details = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE public.usuarios SET nombre=%s, apellido=%s, correo=%s, telefono=%s, tipo_usuario=%s, contrasena=%s WHERE id=%s RETURNING id",
            (user_details['nombre'], user_details['apellido'], user_details['correo'], user_details['telefono'], user_details['tipo_usuario'], user_details['contrasena'], user_id)
        )
        updated_user = cursor.fetchone()
        if updated_user is None:
            response = ResponseFactory.create_response('not_found', 'Usuario no encontrado')
            return _corsify_actual_response(response)
        conn.commit()
        response = ResponseFactory.create_response('success', 'Usuario actualizado exitosamente')
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

@app.route('/user/<int:user_id>', methods=['DELETE', 'OPTIONS'])
def delete_user(user_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM public.usuarios WHERE id = %s RETURNING id", (user_id,))
        deleted_user = cursor.fetchone()
        if deleted_user is None:
            response = ResponseFactory.create_response('not_found', 'Usuario no encontrado')
            return _corsify_actual_response(response)
        conn.commit()
        response = ResponseFactory.create_response('success', 'Usuario eliminado exitosamente')
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=3200)
