# backend/microservicios_auditoria/app.py
from flask_cors import CORS
from flask import Flask, jsonify, make_response
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'tu_super_secreto'
CORS(app, resources={r"/*": {"origins": "*"}})

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
                password="admin",
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

def _corsify_actual_response(response):
    if isinstance(response, tuple):
        response, status = response
        response = make_response(response, status)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/auditoria', methods=['GET'])
def get_auditoria():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT * FROM public.auditoria")
        records = cursor.fetchall()
        response = ResponseFactory.create_response('success', 'Registros de auditoría obtenidos con éxito', records)
        return _corsify_actual_response(response)
    except psycopg2.DatabaseError as e:
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=3400)
