import sqlite3
import configparser
import os
from utils.logger import get_logger # Importa el logger que acabamos de crear

# Obtenemos un logger para este módulo
logger = get_logger(__name__)

# --- Configuración de la Base de Datos ---
# Obtenemos el nombre de la BD desde config.ini
config = configparser.ConfigParser()
# Ruta al config.ini (subiendo un nivel desde /utils)
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
config.read(config_path)

DB_NAME = config.get('DB', 'NAME', fallback='test_results.db')
# Ruta completa a la BD en la raíz del proyecto
DB_PATH = os.path.join(os.path.dirname(__file__), '..', DB_NAME)


def create_connection():
    """Crea una conexión a la base de datos SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        logger.error(f"Error al conectar a SQLite en '{DB_PATH}': {e}")
    return conn

def create_table(conn):
    """Crea la tabla de resultados si no existe."""
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL,
            url_version TEXT NOT NULL,
            status TEXT NOT NULL,
            duration REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """
    try:
        c = conn.cursor()
        c.execute(sql_create_table)
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error al crear la tabla: {e}")

def insert_result(test_name, url_version, status, duration, booking_reference=None):
    """
    Inserta el resultado de la prueba en la base de datos.
    (Llamado automáticamente por conftest.py)
    """
    conn = create_connection()
    if conn:
        with conn:
            # Asegurarse de que la tabla exista antes de insertar
            create_table(conn) 
            
            sql = ''' INSERT INTO test_results(test_name, url_version, status, duration)
                      VALUES(?,?,?,?) '''
            try:
                cur = conn.cursor()
                cur.execute(sql, (test_name, url_version, status, duration))
                conn.commit()
                logger.debug(f"Resultado insertado en BD: {test_name}, {status}")
            except sqlite3.Error as e:
                logger.error(f"Error al insertar en BD: {e}")
    else:
        logger.error("No se pudo crear la conexión a la base de datos para insertar el resultado.")