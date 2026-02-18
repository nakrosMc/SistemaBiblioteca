import os
from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv  # <--- Importamos esto

# Cargar las variables del archivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de la Base de Datos usando variables de entorno
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def get_db_connection():
    try:
        # **DB_CONFIG desempaqueta el diccionario
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error conectando a la BD: {e}")
        return None

@app.route('/api/proyectos', methods=['GET'])
def obtener_proyectos():
    conn = get_db_connection()
    
    if conn is None:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            p.titulo,
            p.fecha,
            p.disponibilidad,
            c.nombre as carrera,
            t.nombre as tutor,
            STRING_AGG(a.nombre, ', ') as autor
        FROM proyectos p
        JOIN carreras c ON p.carrera_id = c.id
        JOIN tutores t ON p.tutor_id = t.id
        JOIN proyecto_autores pa ON p.id = pa.proyecto_id
        JOIN autores a ON pa.autor_id = a.id
        GROUP BY p.id, p.titulo, p.fecha, p.disponibilidad, c.nombre, t.nombre
        ORDER BY p.titulo;
    """
    
    try:
        cur.execute(query)
        proyectos = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(proyectos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
