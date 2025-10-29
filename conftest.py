import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from utils.logger import get_logger
from utils.db_manager import insert_result
import time
import allure
import configparser
import os

# --- Leer las URLs del config.ini ---
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

NUXQA4_URL = config.get('URLs', 'NUXQA4')
NUXQA5_URL = config.get('URLs', 'NUXQA5')

# --- 1. Fixture base_url (Parametrizada) ---
@pytest.fixture(scope="session", params=[NUXQA4_URL, NUXQA5_URL])
def base_url(request):
    """
    Fixture para proveer las URLs (NUXQA4 y NUXQA5).
    El test se ejecutará una vez por cada URL.
    """
    return request.param

# --- 2. Fixture Logger ---
@pytest.fixture(scope="session")
def logger():
    """Fixture para inyectar el logger en los tests."""
    return get_logger() 

# --- 3. Fixture WebDriver (Session-scoped) ---
@pytest.fixture(scope="session")
def setup_browser():
    """Configura el WebDriver (Chrome) una vez por sesión."""
    chrome_options = ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options) 
    driver.implicitly_wait(10)
    driver.maximize_window()
    yield driver
    driver.quit()

# --- 4. Fixture Driver (Function-scoped) ---
@pytest.fixture(scope="function")
def driver(setup_browser, base_url):
    """
    Proporciona un driver limpio para cada test, 
    navegando a la URL base antes de empezar.
    """
    setup_browser.get(base_url)
    yield setup_browser

# --- 5. Hook para SQLite y Screenshots (CORREGIDO) ---
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == 'call':
        
        # --- CORRECCIÓN para leer 'start_time' ---
        # Buscar el 'start_time' en la lista de user_properties
        start_time = time.time() # Default por si falla la búsqueda
        for prop in item.user_properties:
            if prop[0] == 'start_time':
                start_time = prop[1]
                break
        # --- FIN CORRECCIÓN ---
        
        duration = time.time() - start_time
        test_name = item.name
        status = report.outcome.upper()
        
        # Obtener la URL versionada
        base_url_fixture = item.funcargs.get('base_url', 'N/A')
        url_version = 'NuxQA4' if 'nuxqa4' in base_url_fixture else ('NuxQA5' if 'nuxqa5' in base_url_fixture else 'N/A')
        
        insert_result(test_name, url_version, status, duration)
        
        # Adjuntar screenshot a Allure SÓLO si el test falla
        if report.failed:
            try:
                driver = item.funcargs['driver']
                screenshot = driver.get_screenshot_as_png()
                allure.attach(
                    screenshot,
                    name=f"Fallo_{test_name}",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                print(f"Error al adjuntar screenshot: {e}")

# --- CORRECCIÓN para guardar 'start_time' ---
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """
    Guarda el tiempo de inicio para el cálculo de duración.
    (CORREGIDO: usa .append() en lugar de asignación de dict)
    """
    item.user_properties.append(('start_time', time.time()))