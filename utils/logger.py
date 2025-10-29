import logging
import os
import sys

def get_logger(name='test_logger'):
    """
    Configura y devuelve un logger con handlers 
    para consola y archivo.
    """
    # Crear el directorio de logs si no existe
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'test_execution.log')

    # Crear el logger
    logger = logging.getLogger(name)
    
    # Evitar que se dupliquen los handlers si ya existe
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG) # Nivel más bajo para capturar todo

    # --- Formateador ---
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # --- Handler para Archivo (DEBUG) ---
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG) # Guardar todo en el archivo
    file_handler.setFormatter(formatter)
    
    # --- Handler para Consola (INFO) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO) # Mostrar solo INFO y superior
    console_handler.setFormatter(formatter)

    # Añadir handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger