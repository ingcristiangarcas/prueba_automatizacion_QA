# pages/passenger_page_rt.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.logger import get_logger
import time
import allure

logger = get_logger()

# --- ESTRATEGIA: MEDIDAS DESESPERADAS (FULL XPATH) ---

def full_xpath_name_locator(i):
    """
    Devuelve el Full XPath para el NOMBRE del Adulto {i}
    """
    return (By.XPATH, f"/html/body/div[1]/main/div/div[3]/div/div/passenger-details-container/personal-data-custom/div/div/div[{i}]/personal-data-form-custom/div/base-form/panel/div/panel-content/form-editor/panel/div/panel-content/base-form-editor/form/div[2]/div[1]/div/div[1]/div/div[2]/ibe-input/div/div/input")

def full_xpath_lastname_locator(i):
    """
    Devuelve el Full XPath para el APELLIDO del Adulto {i}
    """
    return (By.XPATH, f"/html/body/div[1]/main/div/div[3]/div/div/passenger-details-container/personal-data-custom/div/div/div[{i}]/personal-data-form-custom/div/base-form/panel/div/panel-content/form-editor/panel/div/panel-content/base-form-editor/form/div[2]/div[1]/div/div[2]/ibe-input/div/div/input")

# --- ¡NUEVO PASO 2: GÉNERO! ---

def full_xpath_gender_dropdown_locator(i):
    """
    Devuelve el Full XPath para el BOTÓN DEL DROPDOWN 'GÉNERO' del Adulto {i}
    """
    return (By.XPATH, f"/html/body/div[1]/main/div/div[3]/div/div/passenger-details-container/personal-data-custom/div/div/div[{i}]/personal-data-form-custom/div/base-form/panel/div/panel-content/form-editor/panel/div/panel-content/base-form-editor/form/div[2]/div[1]/div/div[1]/div/div[1]/ibe-select-custom/div/div[2]/button")

def full_xpath_gender_option_locator(i, gender_text):
    """
    Devuelve el Full XPath para la OPCIÓN 'Masculino' o 'Femenino' del Adulto {i}.
    Nota: Apuntamos al <button>, no al <span> interno, para asegurar el clic.
    """
    # Elige li[1] para Masculino, li[2] para Femenino
    option_index = "1" if gender_text == "Masculino" else "2"
    
    return (By.XPATH, f"/html/body/div[1]/main/div/div[3]/div/div/passenger-details-container/personal-data-custom/div/div/div[{i}]/personal-data-form-custom/div/base-form/panel/div/panel-content/form-editor/panel/div/panel-content/base-form-editor/form/div[2]/div[1]/div/div[1]/div/div[1]/ibe-select-custom/div/div[2]/ul/li[{option_index}]/button")

# ---

class PassengersPageRT(BasePage):
    """
    Página de Pasajeros para RoundTrip (Modo Recursivo)
    Objetivo: Llenar Nombres, Apellidos y GÉNERO usando Full XPath.
    """
    
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")

    def __init__(self, driver):
        super().__init__(driver)

    @allure.step("PASO 2: Rellenar 9 Nombres, Apellidos y GÉNEROS (Modo Full XPath)")
    def fill_all_names_lastnames_and_genders(self, passengers_data: list):
        """
        Rellena NOMBRES, APELLIDOS y GÉNERO para los 9 pasajeros.
        """
        wait = WebDriverWait(self.driver, 45) 
        
        logger.info("Esperando a que la página de pasajeros cargue...")
        try:
            wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
            logger.info("Page loader desapareció.")
        except:
            logger.warning("El 'page loader' no desapareció. Continuando...")
            pass
        
        total_pax = len(passengers_data)
        logger.info(f">>> [MODO RECURSIVO 2] Iniciando llenado de {total_pax} Nombres/Apellidos/Géneros...")

        for i, pax_data in enumerate(passengers_data, start=1):
            logger.info(f"--- Procesando Pasajero {i}/{total_pax} ---")
            
            try:
                # 1. Definir locators Full XPath
                name_locator = full_xpath_name_locator(i)
                lastname_locator = full_xpath_lastname_locator(i)
                gender_dropdown_loc = full_xpath_gender_dropdown_locator(i)
                
                # Determinar qué opción de género buscar
                gender_text = "Masculino" if pax_data['gender'] != "Femenino" else "Femenino"
                gender_option_loc = full_xpath_gender_option_locator(i, gender_text)

                # 2. ENCONTRAR Y HACER SCROLL
                logger.info(f"[Pax {i}] Buscando (Full XPath) input de nombre para hacer scroll...")
                name_element = wait.until(EC.presence_of_element_located(name_locator))
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", name_element)
                logger.info(f"[Pax {i}] Scroll a input de nombre. Pausando 0.5s...")
                time.sleep(0.5) 

                # 3. ESCRIBIR NOMBRE
                name_element.send_keys(pax_data['first_name'])
                logger.info(f"[Pax {i}] Nombre '{pax_data['first_name']}' escrito.")
                
                # 4. ESCRIBIR APELLIDO
                self.do_send_keys(lastname_locator, pax_data['last_name'])
                logger.info(f"[Pax {i}] Apellido '{pax_data['last_name']}' escrito.")
                
                # --- ¡NUEVO PASO! ---
                # 5. SELECCIONAR GÉNERO
                logger.info(f"[Pax {i}] Haciendo clic en dropdown de Género...")
                self.js_click(gender_dropdown_loc)
                
                logger.info(f"[Pax {i}] Pausando 0.5s para que aparezca el menú...")
                time.sleep(0.5) # Pausa VITAL para que el <ul> aparezca
                
                logger.info(f"[Pax {i}] Esperando y haciendo clic en la opción '{gender_text}'...")
                wait.until(EC.element_to_be_clickable(gender_option_loc))
                self.js_click(gender_option_loc)
                # --- FIN NUEVO PASO ---
                
                logger.info(f"[Pax {i}] ¡ÉXITO!")

            except Exception as e:
                logger.error(f"Error llenando (Full XPath) al Pasajero {i}: {e}")
                self.take_screenshot(f"error_pax_{i}_full_xpath.png")
                raise 

        logger.info(f"¡Todos los {total_pax} nombres, apellidos y géneros se han rellenado!")
        
        logger.info("Test de 'Paso 2' terminado. Pausando 10s para revisión visual...")
        time.sleep(10)