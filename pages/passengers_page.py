# pages/passengers_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from pages.base_page import BasePage
from utils.logger import get_logger
from faker import Faker
import time
import allure

logger = get_logger()

# --- MAPA DE MESES ---
MONTH_MAP = {
    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
}

# --- FUNCIONES LOCALIZADORAS (Movidas afuera) ---
def first_name_input_locator(i):
    return (By.XPATH, f"(//input[contains(@id, 'IdFirstName')])[{i}]")
def last_name_input_locator(i):
    return (By.XPATH, f"(//input[contains(@id, 'IdLastName')])[{i}]")
def gender_dropdown_locator(i):
    return (By.XPATH, f"(//button[contains(@id, 'IdPaxGender')])[{i}]")
def dob_day_dropdown_locator(i):
    return (By.XPATH, f"(//button[contains(@id, 'dateDayId')])[{i}]")
def dob_month_dropdown_locator(i):
    return (By.XPATH, f"(//button[contains(@id, 'dateMonthId')])[{i}]")
def dob_year_dropdown_locator(i):
    return (By.XPATH, f"(//button[contains(@id, 'dateYearId')])[{i}]")
def dob_option_locator(text):
    return (By.XPATH, f"//button[.//span[normalize-space()='{text}']]")
def doc_type_dropdown_locator(i):
    return (By.XPATH, f"(//button[contains(@id, 'IdDocType')])[{i}]")
def doc_type_option_locator(doc_type):
    return (By.XPATH, f"//button[.//span[normalize-space()=\"{doc_type}\"]]")
def doc_number_input_locator(i):
    return (By.XPATH, f"(//input[contains(@id, 'IdDocNum')])[{i}]")
def nationality_dropdown_locator(i):
    return (By.XPATH, f"(//button[contains(@id, 'IdDocNationality')])[{i}]")
def frequent_flyer_dropdown_locator(i):
    return (By.XPATH, f"(//button[contains(@id, 'customerPrograms')])[{i}]")
# ---

class PassengersPage(BasePage):
    
    # --- LOCATORS (Estáticos) ---
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    # --- GÉNERO (Actualizado) ---
    GENDER_OPTION_MALE = (By.XPATH, "//button[.//span[normalize-space()='Masculino']]")
    GENDER_OPTION_FEMALE = (By.XPATH, "//button[.//span[normalize-space()='Femenino']]") # <-- AÑADIDO
    # ---
    NATIONALITY_OPTION_COLOMBIA = (By.XPATH, "//button[.//span[normalize-space()='Colombia']]")
    FREQ_FLYER_OPTION_NO_APLICA = (By.XPATH, "//button[.//span[normalize-space()='No aplica']]")
    CONTACT_TITULAR_DROPDOWN = (By.ID, "passengerId")
    CONTACT_TITULAR_OPTION_TEST = (By.ID, "passengerId-0") 
    CONTACT_PREFIX_DROPDOWN = (By.ID, "phone_prefixPhoneId")
    CONTACT_PREFIX_COLOMBIA = (By.ID, "phone_prefixPhoneId-1") 
    CONTACT_PHONE_INPUT = (By.ID, "phone_phoneNumberId")
    CONTACT_EMAIL_INPUT = (By.ID, "email")
    CONTACT_CONFIRM_EMAIL_INPUT = (By.ID, "confirmEmail")
    CONTACT_TERMS_CHECKBOX = (By.ID, "sendNewsLetter") 
    CONTINUE_BUTTON = (By.XPATH, "//button[contains(@class, 'page_button') and .//span[normalize-space()='Continuar']]")


    def __init__(self, driver):
        super().__init__(driver)
        self.faker = Faker('es_CO') 

    @allure.step("Rellenar página de Pasajeros y Contacto")
    def fill_all_data_and_continue(self, passengers_data: list):
        self.fill_passengers_forms(passengers_data)
        if passengers_data:
            self.fill_contact_data(passengers_data[0]) 
        self.click_continue()
        
    def fill_passengers_forms(self, passengers_data: list):
        """
        Rellena los formularios para CADA pasajero en la lista.
        (Versión con scroll robusto y js_click)
        """
        wait = WebDriverWait(self.driver, 30)
        logger.info("Esperando a que la página de pasajeros cargue...")
        try: wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
        except: pass
        
        first_name_locator = first_name_input_locator(1)
        wait.until(EC.visibility_of_element_located(first_name_locator))
        
        for i, passenger in enumerate(passengers_data):
            pax_index = i + 1 
            
            logger.info(f"Rellenando datos del Pasajero {pax_index}: {passenger['first_name']} {passenger['last_name']}")
            
            day, month_num, year = passenger['dob'].split('/')
            month_text = MONTH_MAP[month_num] 

            # --- Rellenar Formulario ---
            try:
                name_input = wait.until(EC.visibility_of_element_located(first_name_input_locator(pax_index)))
                # Hacemos scroll al elemento para centrarlo
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", name_input)
                time.sleep(0.5)
            except Exception: pass

            self.do_send_keys(first_name_input_locator(pax_index), passenger['first_name'])
            self.do_send_keys(last_name_input_locator(pax_index), passenger['last_name'])
            
            # --- LÓGICA DE GÉNERO CORREGIDA (usando js_click) ---
            self.js_click(gender_dropdown_locator(pax_index)); time.sleep(0.5)
            
            # Ahora leemos la clave 'gender' que SÍ existe
            if passenger['gender'] == 'Femenino':
                logger.info(f"Seleccionando género: Femenino (Pax {pax_index})")
                self.js_click(self.GENDER_OPTION_FEMALE)
            else:
                logger.info(f"Seleccionando género: Masculino (Pax {pax_index})")
                self.js_click(self.GENDER_OPTION_MALE)
            time.sleep(0.5) 
            # --- FIN CORRECCIÓN ---
            
            # Usamos js_click para todos los dropdowns para evitar intercepciones
            self.js_click(dob_day_dropdown_locator(pax_index)); time.sleep(0.5)
            self.js_click(dob_option_locator(day))
            
            self.js_click(dob_month_dropdown_locator(pax_index)); time.sleep(0.5)
            self.js_click(dob_option_locator(month_text))
            
            self.js_click(dob_year_dropdown_locator(pax_index)); time.sleep(0.5)
            self.js_click(dob_option_locator(year))
            
            # --- Rellenar Documentos ---
            logger.info(f"Rellenando Documento: {passenger['doc_type']} - {passenger['doc_number']}")
            try:
                self.js_click(doc_type_dropdown_locator(pax_index)); time.sleep(0.5)
                self.js_click(doc_type_option_locator(passenger['doc_type'])) 
                self.do_send_keys(doc_number_input_locator(pax_index), passenger['doc_number'])
            except Exception as e:
                logger.error(f"Error al rellenar documento para Pax {pax_index}: {e}")
                self.take_screenshot(f"error_documento_pax_{pax_index}.png")
                raise 
            
            # --- Rellenar Nacionalidad (CON SCROLL y JS_CLICK) ---
            logger.info(f"Haciendo scroll y rellenando Nacionalidad para Pax {pax_index}")
            try:
                nationality_dropdown = wait.until(EC.presence_of_element_located(nationality_dropdown_locator(pax_index)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", nationality_dropdown)
                self.js_click(nationality_dropdown_locator(pax_index)); time.sleep(0.5)
                self.js_click(self.NATIONALITY_OPTION_COLOMBIA)
            except Exception as e:
                 logger.error(f"Error al rellenar nacionalidad para Pax {pax_index}: {e}")
                 self.take_screenshot(f"error_nacionalidad_pax_{pax_index}.png")
                 raise
            
            # --- Rellenar Viajero Frecuente (Opcional) ---
            try:
                logger.info("Seleccionando 'No aplica' para viajero frecuente.")
                ff_dropdown = wait.until(EC.presence_of_element_located(frequent_flyer_dropdown_locator(pax_index)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", ff_dropdown)
                self.js_click(frequent_flyer_dropdown_locator(pax_index)); time.sleep(0.5)
                self.js_click(self.FREQ_FLYER_OPTION_NO_APLICA)
            except Exception as e:
                logger.warning(f"No se pudo seleccionar 'No aplica' para viajero frecuente (Pax {pax_index}): {e}")
            
            logger.info(f"Pasajero {pax_index} completado.")
            time.sleep(1) 

            
    def fill_contact_data(self, contact_pax_data):
        # ... (código existente, sin cambios) ...
        logger.info("Rellenando datos de contacto del titular."); phone_number = contact_pax_data.get('phone', f"315{self.faker.random_number(digits=7, fix_len=True)}"); email = contact_pax_data.get('email', self.faker.email())
        try: contact_input = self.driver.find_element(*self.CONTACT_PHONE_INPUT); self.driver.execute_script("arguments[0].scrollIntoView(true);", contact_input); time.sleep(1)
        except Exception as e: logger.warning(f"No se pudo hacer scroll a la sección de contacto: {e}")
        try: logger.info("Seleccionando titular 'Test Test'..."); self.js_click(self.CONTACT_TITULAR_DROPDOWN); time.sleep(0.5); self.js_click(self.CONTACT_TITULAR_OPTION_TEST)
        except Exception as e: logger.error(f"No se pudo seleccionar a 'Test Test' como titular: {e}"); raise
        self.js_click(self.CONTACT_PREFIX_DROPDOWN); time.sleep(0.5); self.js_click(self.CONTACT_PREFIX_COLOMBIA)
        self.do_send_keys(self.CONTACT_PHONE_INPUT, phone_number); self.do_send_keys(self.CONTACT_EMAIL_INPUT, email); self.do_send_keys(self.CONTACT_CONFIRM_EMAIL_INPUT, email)
        logger.info("Aceptando términos (clic en checkbox)."); self.js_click(self.CONTACT_TERMS_CHECKBOX); time.sleep(1)

    def click_continue(self):
        # ... (código existente, sin cambios) ...
        logger.info("Haciendo clic en Continuar para ir a la página de servicios con JS Force Click."); wait = WebDriverWait(self.driver, 20)
        try:
            continue_btn = wait.until(EC.presence_of_element_located(self.CONTINUE_BUTTON)); self.driver.execute_script("arguments[0].scrollIntoView(true);", continue_btn); time.sleep(1) 
            self.driver.execute_script("arguments[0].click();", continue_btn); logger.info("Clic forzado en 'Continuar' realizado.")
        except Exception as e: logger.error(f"Falló el clic en Continuar: {e}"); self.take_screenshot("error_clic_continuar_pax.png"); raise