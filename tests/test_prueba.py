import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Imports para la configuración ---
from selenium.webdriver.chrome.service import Service  # <--- 1. IMPORTA 'Service'
from webdriver_manager.chrome import ChromeDriverManager
# -----------------------------------

# Importar la clase 'Select', que es clave para esto
from selenium.webdriver.support.ui import Select

# --- Configuración del WebDriver (Automática con webdriver-manager) ---
# Esta línea instala o encuentra el chromedriver automáticamente
chrome_service = Service(ChromeDriverManager().install()) # <--- 2. DEFINE 'chrome_service'

# Ahora esta línea SÍ funciona
driver = webdriver.Chrome(service=chrome_service)
driver.maximize_window()

print("¡WebDriver iniciado correctamente!")
# driver.get("...")

def seleccionar_opcion_reset(driver_instance, select_full_xpath):
    """
    Navega a una URL, busca un <select> por su XPath y selecciona 
    la opción con el texto visible (label) "reset".
    
    :param driver_instance: La instancia del WebDriver de Selenium.
    :param page_url: La URL de la página a la que se debe navegar.
    :param select_full_xpath: El XPath completo hasta el elemento <select>.
    """
    wait = WebDriverWait(driver_instance, 10)
    
    try:
       
        
        # 2. Esperar a que el elemento <select> esté presente en la página
        print(f"Buscando el <select> con XPath: {select_full_xpath}")
        select_element = wait.until(
            EC.presence_of_element_located((By.XPATH, select_full_xpath))
        )
        
        # 3. Usar la clase Select de Selenium para "envolver" el elemento
        #    Esto nos da métodos especiales como .select_by_visible_text()
        select_obj = Select(select_element)
        
        # 4. Seleccionar la opción por su texto visible (label)
        print("Intentando seleccionar la opción 'reset'...")
        select_obj.select_by_visible_text("Masculino")
        
        print("\n¡Éxito! La opción 'reset' fue seleccionada.")
        
    except TimeoutException:
        print(f"\nError: No se pudo encontrar el elemento <select> en 10 segundos.")
        print("Verifica que el XPath sea correcto y la página haya cargado.")
        
    except NoSuchElementException:
        # Este error ocurre si el <select> se encontró, pero la opción 
        # "reset" NO existe dentro de él.
        print(f"\nError: Se encontró el <select>, pero no tiene una opción")
        print("con el texto visible 'reset'.")
        
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")

# --- CÓMO USAR LA FUNCIÓN ---

# 1. DEFINE TUS VARIABLES
# La URL de la página donde está el formulario
PAGE_URL = "https://codebeautify.org/html-button-generator"

# El XPath completo de tu lista <select>
# (Estoy usando un ejemplo de la página de arriba)
SELECT_FULL_XPATH = "/html/body/div[1]/section[2]/div[3]/div[1]/form/div[1]/div[2]/div/div/div/select"

# 2. EJECUTAR LA FUNCIÓN
try:
    seleccionar_opcion_reset(driver, PAGE_URL, SELECT_FULL_XPATH)
    
    # Pausa para que veas el resultado antes de cerrar
    time.sleep(10)

finally:
    # 3. CERRAR EL NAVEGADOR
    print("Cerrando el navegador.")
    driver.quit()