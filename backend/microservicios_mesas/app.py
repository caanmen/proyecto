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

@app.route('/mesas', methods=['POST', 'OPTIONS'])
def crear_mesa():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    data = request.get_json()
    numero_mesa = data['numero_mesa']
    personas = data['personas']
    localizacion = data['localizacion']
    usuario_responsable = data['usuario_responsable']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO mesas (numero_mesa, personas, localizacion, disponible, usuario_responsable, reserva_id) VALUES (%s, %s, %s, True, %s, NULL) RETURNING numero_mesa;',
            (numero_mesa, personas, localizacion, usuario_responsable)
        )
        numero_mesa = cursor.fetchone()[0]
        conn.commit()
        response = ResponseFactory.create_response('success', 'Mesa creada con éxito', {"numero_mesa": numero_mesa})
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        conn.rollback()
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

@app.route('/mesas/<int:numero_mesa>', methods=['PUT', 'OPTIONS'])
def actualizar_mesa(numero_mesa):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    data = request.get_json()
    personas = data.get('personas')
    localizacion = data.get('localizacion')
    disponible = data.get('disponible', True)
    usuario_responsable = data['usuario_responsable']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT reserva_id FROM mesas WHERE numero_mesa = %s", (numero_mesa,))
        mesa_info = cursor.fetchone()
        if mesa_info and mesa_info['reserva_id'] is not None and disponible:
            response = ResponseFactory.create_response('error', "No se puede marcar como disponible una mesa reservada")
            return _corsify_actual_response(response)

        cursor.execute(
            "UPDATE mesas SET personas = %s, localizacion = %s, disponible = %s, usuario_responsable = %s WHERE numero_mesa = %s RETURNING numero_mesa;",
            (personas, localizacion, disponible, usuario_responsable, numero_mesa)
        )
        updated_mesa = cursor.fetchone()
        if not updated_mesa:
            response = ResponseFactory.create_response('not_found', "Mesa no encontrada")
            return _corsify_actual_response(response)
        conn.commit()
        response = ResponseFactory.create_response('success', "Mesa actualizada con éxito", {"numero_mesa": updated_mesa[0]})
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        conn.rollback()
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

@app.route('/mesas/<int:numero_mesa>', methods=['GET', 'OPTIONS'])
def get_mesa(numero_mesa):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT numero_mesa, personas, localizacion, disponible, usuario_responsable FROM mesas WHERE numero_mesa = %s", (numero_mesa,))
        mesa = cursor.fetchone()
        if mesa:
            mesa_info = {
                'numero_mesa': mesa[0],
                'personas': mesa[1],
                'localizacion': mesa[2],
                'disponible': mesa[3],
                'usuario_responsable': mesa[4]
            }
            response = ResponseFactory.create_response('success', 'Mesa encontrada', mesa_info)
            return _corsify_actual_response(response)
        else:
            response = ResponseFactory.create_response('not_found', 'Mesa no encontrada')
            return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

@app.route('/mesas', methods=['GET', 'OPTIONS'])
def get_mesas():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT numero_mesa, personas, localizacion, disponible, usuario_responsable, reserva_id FROM public.mesas")
        mesas = cursor.fetchall()
        response = ResponseFactory.create_response('success', 'Mesas obtenidas con éxito', mesas)
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

@app.route('/mesas/<int:numero_mesa>', methods=['DELETE', 'OPTIONS'])
def delete_mesa(numero_mesa):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM mesas WHERE numero_mesa = %s RETURNING numero_mesa;", (numero_mesa,))
        deleted_mesa = cursor.fetchone()
        if not deleted_mesa:
            response = ResponseFactory.create_response('not_found', "Mesa no encontrada")
            return _corsify_actual_response(response)
        conn.commit()
        response = ResponseFactory.create_response('success', "Mesa eliminada con éxito")
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        conn.rollback()
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=3300)
