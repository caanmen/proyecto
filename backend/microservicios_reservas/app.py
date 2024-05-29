from flask_cors import CORS
from flask import Flask, request, jsonify, make_response
import psycopg2
import psycopg2.extras
from datetime import datetime, date, time

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
        if data:
            data = serialize_data(data)
        if response_type == 'success':
            return jsonify({'status': 'success', 'message': message, 'data': data}), 200
        elif response_type == 'error':
            return jsonify({'status': 'error', 'message': message}), 400
        elif response_type == 'not_found':
            return jsonify({'status': 'not_found', 'message': message}), 404

def serialize_data(data):
    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, (datetime, date, time)):
        return data.isoformat()
    return data

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response

def _corsify_actual_response(response):
    if not isinstance(response, tuple):
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    else:
        resp, status = response
        response = make_response(resp, status)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

@app.route('/')
def home():
    return 'Bienvenido a la API de ReservaFacil!'

@app.route('/reservas', methods=['GET', 'OPTIONS'])
def get_reservas():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT id, fecha, hora, estado, detalle, usuario_responsable, numero_mesa FROM public.reservas")
        reservas = cursor.fetchall()
        response = ResponseFactory.create_response('success', 'Reservas obtenidas con éxito', reservas)
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

@app.route('/create_reserva', methods=['POST', 'OPTIONS'])
def create_reserva():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(
            'SELECT * FROM reservas WHERE fecha = %s AND hora = %s AND numero_mesa = %s',
            (data['fecha'], data['hora'], data['numero_mesa'])
        )
        existing_reserva = cursor.fetchone()
        if existing_reserva:
            response = ResponseFactory.create_response('error', 'Ya existe una reserva para esta mesa en la fecha y hora seleccionadas.')
            return _corsify_actual_response(response)
        
        cursor.execute(
            'INSERT INTO reservas (fecha, hora, estado, detalle, usuario_responsable, numero_mesa) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, fecha, hora, estado, detalle, usuario_responsable, numero_mesa;',
            (data['fecha'], data['hora'], data['estado'], data['detalle'], data['usuario_responsable'], data['numero_mesa'])
        )
        new_reserva = cursor.fetchone()
        conn.commit()
        response = ResponseFactory.create_response('success', 'Reserva creada con éxito', new_reserva)
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        conn.rollback()
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

@app.route('/update_reserva/<int:reserva_id>', methods=['PUT', 'OPTIONS'])
def update_reserva(reserva_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(
            'SELECT * FROM reservas WHERE fecha = %s AND hora = %s AND numero_mesa = %s AND id != %s',
            (data['fecha'], data['hora'], data['numero_mesa'], reserva_id)
        )
        existing_reserva = cursor.fetchone()
        if existing_reserva:
            response = ResponseFactory.create_response('error', 'Ya existe una reserva para esta mesa en la fecha y hora seleccionadas.')
            return _corsify_actual_response(response)
        
        cursor.execute(
            'UPDATE reservas SET fecha = %s, hora = %s, estado = %s, detalle = %s, usuario_responsable = %s, numero_mesa = %s WHERE id = %s RETURNING id, fecha, hora, estado, detalle, usuario_responsable, numero_mesa;',
            (data['fecha'], data['hora'], data['estado'], data['detalle'], data['usuario_responsable'], data['numero_mesa'], reserva_id)
        )
        updated_reserva = cursor.fetchone()
        conn.commit()
        response = ResponseFactory.create_response('success', 'Reserva actualizada con éxito', updated_reserva)
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        conn.rollback()
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_reserva/<int:reserva_id>', methods=['DELETE', 'OPTIONS'])
def delete_reserva(reserva_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT numero_mesa FROM reservas WHERE id = %s", (reserva_id,))
        reserva = cursor.fetchone()
        if reserva:
            cursor.execute("DELETE FROM reservas WHERE id = %s RETURNING id;", (reserva_id,))
            deleted_id = cursor.fetchone()
            if deleted_id:
                cursor.execute(
                    "UPDATE mesas SET disponible = True WHERE numero_mesa = %s;",
                    (reserva['numero_mesa'],)
                )
            conn.commit()
            response = ResponseFactory.create_response('success', 'Reserva eliminada con éxito')
            return _corsify_actual_response(response)
        else:
            response = ResponseFactory.create_response('not_found', 'Reserva no encontrada')
            return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        conn.rollback()
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=3100)
