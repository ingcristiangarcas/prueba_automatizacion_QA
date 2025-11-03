# pages/passenger_page_rt.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException # Importado para manejo de errores
from pages.base_page import BasePage
from utils.logger import get_logger
import time
import allure
import random 
# ¡Importamos nuestra nueva "Biblioteca" de Locators!
from . import locators_rt 

logger = get_logger()

class PassengersPageRT(BasePage):
    """
    Página de Pasajeros para RoundTrip (Modo Recursivo v3)
    Usa el motor de locators de 'locators_rt.py'
    """
    
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    # --- Locators de Contacto (los que son iguales en ambas) ---
    CONTACT_TITULAR_DROPDOWN = (By.ID, "passengerId")
    CONTACT_TITULAR_OPTION_TEST = (By.ID, "passengerId-0") 
    CONTACT_PREFIX_DROPDOWN = (By.ID, "phone_prefixPhoneId")
    CONTACT_PREFIX_COLOMBIA = (By.ID, "phone_prefixPhoneId-1") 
    CONTACT_PHONE_INPUT = (By.ID, "phone_phoneNumberId")
    CONTACT_EMAIL_INPUT = (By.ID, "email")
    CONTACT_CONFIRM_EMAIL_INPUT = (By.ID, "confirmEmail")
    
    # <<< CORREGIDO: Se eliminó CONTACT_TERMS_CHECKBOX de aquí >>>
    
    CONTINUE_BUTTON = (By.XPATH, "//button[contains(@class, 'page_button') and .//span[normalize-space()='Continuar']]")


    def __init__(self, driver):
        super().__init__(driver)
        self.current_url = driver.current_url
        if "nuxqa4" in self.current_url:
            self.url_type = 'nuxqa4'
        elif "nuxqa5" in self.current_url:
            self.url_type = 'nuxqa5'
        else:
            raise Exception("URL no reconocida. No se pueden cargar locators.")
        logger.info(f"Página de Pasajeros iniciada en MODO: [{self.url_type}]")

    @allure.step("PASO FINAL: Rellenar TODOS los datos de los 9 pasajeros (Modo Biblioteca)")
    def fill_all_passenger_data(self, passengers_data: list):
        """
        Método principal que rellena TODO para los 9 pasajeros.
        """
        wait_long = WebDriverWait(self.driver, 45) 
        
        logger.info("Esperando a que la página de pasajeros cargue...")
        try:
            wait_long.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
            logger.info("Page loader desapareció.")
        except:
            logger.warning("El 'page loader' no desapareció. Continuando...")
            pass
        
        total_pax = len(passengers_data)
        logger.info(f">>> [MODO BIBLIOTECA] Iniciando llenado de {total_pax} pasajeros...")

        for i, pax_data in enumerate(passengers_data, start=1):
            logger.info(f"--- Procesando Pasajero {i}/{total_pax} ---")
            
            wait = WebDriverWait(self.driver, 10)

            try:
                # 1. SCROLL AL PASAJERO
                name_loc_key = f"pax_{i}_name"
                name_loc = locators_rt.get_locator(name_loc_key, self.current_url)
                
                name_element = wait_long.until(EC.element_to_be_clickable(name_loc))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", name_element)
                logger.info(f"[Pax {i}] Scroll a input de nombre.")
                
                # 2. LLENAR FORMULARIO
                self._fill_names(i, pax_data, name_element)
                self._fill_gender(i, pax_data, wait)
                self._fill_dob(i, pax_data, wait)
                
                doc_type_text = pax_data['doc_type']
                if doc_type_text in ["Pasaporte", "Pasaporte diplomático"]:
                    is_passport = True
                else:
                    is_passport = False

                self._fill_document_and_nationality(i, pax_data, is_passport, wait)
                self._fill_frequent_flyer(i, is_passport, wait)
                
                logger.info(f"[Pax {i}] ¡ÉXITO COMPLETO!")

            except Exception as e:
                logger.error(f"Error llenando (Modo Biblioteca) al Pasajero {i}: {e}")
                self.take_screenshot(f"error_pax_{i}_biblioteca.png")
                raise 

        logger.info(f"¡Todos los {total_pax} pasajeros se han rellenado!")
        
        wait_contact = WebDriverWait(self.driver, 10)
        self.fill_contact_data(passengers_data[0], wait_contact)
        self.click_continue()
        
        logger.info("Test de Pasajeros terminado. Navegando a la siguiente página...")

    
    ### --- MÉTODOS AUXILIARES (El "Motor") --- ###
    
    def _fill_names(self, i, pax_data, name_element):
        """Llena nombre y apellido. Recibe el elemento 'name' para no buscarlo de nuevo."""
        lastname_loc = locators_rt.get_locator(f"pax_{i}_lastname", self.current_url)
        
        name_element.send_keys(pax_data['first_name'])
        self.do_send_keys(lastname_loc, pax_data['last_name'])
        logger.info(f"[Pax {i}] Nombre y Apellido escritos.")
    
    def _fill_gender(self, i, pax_data, wait: WebDriverWait):
        """Llena el género."""
        gender_dropdown_loc = locators_rt.get_locator(f"pax_{i}_gender_dropdown", self.current_url)
        gender_text = "Masculino" if pax_data['gender'] != "Femenino" else "Femenino"
        gender_option_loc = locators_rt.get_locator(f"pax_{i}_gender_option_{gender_text.lower()}", self.current_url)

        gender_dropdown_element = wait.until(EC.element_to_be_clickable(gender_dropdown_loc))
        self.driver.execute_script("arguments[0].click();", gender_dropdown_element)
        
        gender_option_element = wait.until(EC.element_to_be_clickable(gender_option_loc))
        self.driver.execute_script("arguments[0].click();", gender_option_element)
        
        logger.info(f"[Pax {i}] Género '{gender_text}' seleccionado.")

    def _fill_dob(self, i, pax_data, wait: WebDriverWait):
        """Llena la fecha de nacimiento completa."""
        dob_data = pax_data['dob'] 
        day, month_num, year = dob_data.split('/') 
        
        logger.info(f"[Pax {i}] Seleccionando Fecha de Nacimiento: {day}/{month_num}/{year}")

        # --- DÍA ---
        day_dropdown_loc = locators_rt.get_locator(f"pax_{i}_dob_day_dropdown", self.current_url)
        day_option_loc = locators_rt.get_locator(f"pax_{i}_dob_day_option_{day}", self.current_url)
        
        day_dropdown_element = wait.until(EC.element_to_be_clickable(day_dropdown_loc))
        self.driver.execute_script("arguments[0].click();", day_dropdown_element)
        day_option_element = wait.until(EC.element_to_be_clickable(day_option_loc))
        self.driver.execute_script("arguments[0].click();", day_option_element)

        # --- MES ---
        month_dropdown_loc = locators_rt.get_locator(f"pax_{i}_dob_month_dropdown", self.current_url)
        month_option_loc = locators_rt.get_locator(f"pax_{i}_dob_month_option_{month_num}", self.current_url)

        month_dropdown_element = wait.until(EC.element_to_be_clickable(month_dropdown_loc))
        self.driver.execute_script("arguments[0].click();", month_dropdown_element)
        month_option_element = wait.until(EC.element_to_be_clickable(month_option_loc))
        self.driver.execute_script("arguments[0].click();", month_option_element)

        # --- AÑO ---
        year_dropdown_loc = locators_rt.get_locator(f"pax_{i}_dob_year_dropdown", self.current_url)
        year_option_loc = locators_rt.get_locator(f"pax_{i}_dob_year_option_{year}", self.current_url)
        
        year_dropdown_element = wait.until(EC.element_to_be_clickable(year_dropdown_loc))
        self.driver.execute_script("arguments[0].click();", year_dropdown_element)
        year_option_element = wait.until(EC.element_to_be_clickable(year_option_loc))
        self.driver.execute_script("arguments[0].click();", year_option_element)
        
        logger.info(f"[Pax {i}] Fecha de Nacimiento seleccionada.")

    def _fill_expiry_date(self, i, wait: WebDriverWait):
        """
        Llena la fecha de expiración.
        """
        day = "10"
        month_num = "10"
        year = "2030"
        logger.info(f"[Pax {i}] Seleccionando Fecha de Expiración: {day}/{month_num}/{year}")

        # --- DÍA (EXP) ---
        day_dropdown_loc = locators_rt.get_locator(f"pax_{i}_exp_day_dropdown", self.current_url)
        day_option_loc = locators_rt.get_locator(f"pax_{i}_exp_day_option_{day}", self.current_url)

        day_dropdown_element = wait.until(EC.element_to_be_clickable(day_dropdown_loc))
        self.driver.execute_script("arguments[0].click();", day_dropdown_element)
        day_option_element = wait.until(EC.element_to_be_clickable(day_option_loc))
        self.driver.execute_script("arguments[0].click();", day_option_element)

        # --- MES (EXP) ---
        month_dropdown_loc = locators_rt.get_locator(f"pax_{i}_exp_month_dropdown", self.current_url)
        month_option_loc = locators_rt.get_locator(f"pax_{i}_exp_month_option_{month_num}", self.current_url)

        month_dropdown_element = wait.until(EC.element_to_be_clickable(month_dropdown_loc))
        self.driver.execute_script("arguments[0].click();", month_dropdown_element)
        month_option_element = wait.until(EC.element_to_be_clickable(month_option_loc))
        self.driver.execute_script("arguments[0].click();", month_option_element)

        # --- AÑO (EXP) ---
        year_dropdown_loc = locators_rt.get_locator(f"pax_{i}_exp_year_dropdown", self.current_url)
        year_option_loc = locators_rt.get_locator(f"pax_{i}_exp_year_option_{year}", self.current_url)

        year_dropdown_element = wait.until(EC.element_to_be_clickable(year_dropdown_loc))
        self.driver.execute_script("arguments[0].click();", year_dropdown_element)
        year_option_element = wait.until(EC.element_to_be_clickable(year_option_loc))
        self.driver.execute_script("arguments[0].click();", year_option_element)
        
        logger.info(f"[Pax {i}] Fecha de Expiración seleccionada.")
        
    def _fill_document_and_nationality(self, i, pax_data, is_passport, wait: WebDriverWait):
        """
        Llena el tipo de doc, número, y la nacionalidad condicional.
        """
        doc_type_text = pax_data['doc_type'] 
        doc_number = pax_data['doc_number'] 
        
        nationality_key = ""
        nationality_text = ""
        
        # --- TIPO DE DOCUMENTO ---
        doc_type_dropdown_loc = locators_rt.get_locator(f"pax_{i}_doc_type_dropdown", self.current_url)
        doc_type_option_loc = locators_rt.get_locator(f"pax_{i}_doc_type_option_{doc_type_text.lower()}", self.current_url)
        
        doc_type_dropdown_element = wait.until(EC.element_to_be_clickable(doc_type_dropdown_loc))
        self.driver.execute_script("arguments[0].click();", doc_type_dropdown_element)
        doc_type_option_element = wait.until(EC.element_to_be_clickable(doc_type_option_loc))
        self.driver.execute_script("arguments[0].click();", doc_type_option_element)
        
        logger.info(f"[Pax {i}] Tipo de Doc '{doc_type_text}' seleccionado.")
        
        
        if doc_type_text == "Pasaporte diplomático":
            try:
                random_letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                random_digits = self.faker.random_number(digits=8, fix_len=True)
                doc_number = f"{random_letter}{random_digits}" 
                logger.info(f"[Pax {i}] 'Pasaporte diplomático' detectado. Generando doc_number aleatorio: {doc_number}")
            except AttributeError:
                logger.warning("self.faker no encontrado. Usando doc_number por defecto para Pasaporte Diplomático.")
                doc_number = "A12345678" 
        

        # --- NÚMERO DE DOCUMENTO ---
        doc_number_input_loc = locators_rt.get_locator(f"pax_{i}_doc_number", self.current_url)
        self.do_send_keys(doc_number_input_loc, doc_number)
        logger.info(f"[Pax {i}] Número de Doc '{doc_number}' escrito.")

        # --- LÓGICA CONDICIONAL ---
        if is_passport:
            try:
                logger.info(f"[Pax {i}] 'Pasaporte' detectado. Intentando rellenar fecha de expiración.")
                self._fill_expiry_date(i, wait)
            except (TimeoutException, Exception) as e:
                logger.warning(f"[Pax {i}] CAMPO 'FECHA DE EXPIRACIÓN' NO ENCONTRADO O FALLÓ. "
                               f"Esto puede ser normal en nuxqa5. Continuando... Error: {e}")
                pass 
            
            nationality_key = f"pax_{i}_nationality_dropdown_shifted"
            
            if doc_type_text == "Pasaporte diplomático":
                nationality_text = "colombia" 
            else: # Pasaporte normal
                nationality_text = "colombia"

            nat_option_key = f"pax_{i}_nationality_option_{nationality_text}_shifted"
        else:
            nationality_key = f"pax_{i}_nationality_dropdown"
            if doc_type_text == "Cédula de extranjería":
                nationality_text = "nicaragua"
            else: # Documento de identidad
                nationality_text = "colombia"
            nat_option_key = f"pax_{i}_nationality_option_{nationality_text}"

        # --- NACIONALIDAD (Ahora usa las claves dinámicas) ---
        nat_dropdown_loc = locators_rt.get_locator(nationality_key, self.current_url)
        nat_option_loc = locators_rt.get_locator(nat_option_key, self.current_url)
        
        nat_dropdown_element = wait.until(EC.element_to_be_clickable(nat_dropdown_loc))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", nat_dropdown_element)
        
        self.driver.execute_script("arguments[0].click();", nat_dropdown_element)
        
        nat_option_element = wait.until(EC.element_to_be_clickable(nat_option_loc))
        self.driver.execute_script("arguments[0].click();", nat_option_element)
        
        logger.info(f"[Pax {i}] Nacionalidad '{nationality_text}' seleccionada.")

    def _fill_frequent_flyer(self, i, is_passport, wait: WebDriverWait):
        """Llena 'No aplica' en viajero frecuente."""
        
        if is_passport:
            flyer_dropdown_key = f"pax_{i}_freq_flyer_dropdown_shifted"
            flyer_option_key = f"pax_{i}_freq_flyer_option_no aplica_shifted"
        else:
            flyer_dropdown_key = f"pax_{i}_freq_flyer_dropdown"
            flyer_option_key = f"pax_{i}_freq_flyer_option_no aplica"
            
        try:
            flyer_dropdown_loc = locators_rt.get_locator(flyer_dropdown_key, self.current_url)
            flyer_option_loc = locators_rt.get_locator(flyer_option_key, self.current_url)

            flyer_dropdown_element = wait.until(EC.element_to_be_clickable(flyer_dropdown_loc))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", flyer_dropdown_element)
            
            self.driver.execute_script("arguments[0].click();", flyer_dropdown_element)
            
            flyer_option_element = wait.until(EC.element_to_be_clickable(flyer_option_loc))
            self.driver.execute_script("arguments[0].click();", flyer_option_element)
            
            logger.info(f"[Pax {i}] Viajero Frecuente 'No aplica' seleccionado.")
        except Exception as e:
            logger.warning(f"[Pax {i}] No se pudo seleccionar 'No aplica' en Viajero Frecuente. Continuando... Error: {e}")
            self.driver.execute_script("window.scrollBy(0, 100);")
            pass 

    def fill_contact_data(self, contact_pax_data, wait: WebDriverWait):
        logger.info("Rellenando datos de contacto del titular.")
        
        phone_number = "3151234567"
        email = "test@test.com"
        try: 
            phone_number = contact_pax_data.get('phone', f"315{self.faker.random_number(digits=7, fix_len=True)}")
            email = contact_pax_data.get('email', self.faker.email())
        except AttributeError:
            logger.warning("self.faker no encontrado en BasePage. Usando datos por defecto.")
            pass
        
        try: 
            contact_input = wait.until(EC.visibility_of_element_located(self.CONTACT_PHONE_INPUT))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", contact_input)
        except: pass
        
        titular_dropdown_element = wait.until(EC.element_to_be_clickable(self.CONTACT_TITULAR_DROPDOWN))
        self.driver.execute_script("arguments[0].click();", titular_dropdown_element)
        titular_option_element = wait.until(EC.element_to_be_clickable(self.CONTACT_TITULAR_OPTION_TEST))
        self.driver.execute_script("arguments[0].click();", titular_option_element)
        
        prefix_dropdown_element = wait.until(EC.element_to_be_clickable(self.CONTACT_PREFIX_DROPDOWN))
        self.driver.execute_script("arguments[0].click();", prefix_dropdown_element)
        prefix_option_element = wait.until(EC.element_to_be_clickable(self.CONTACT_PREFIX_COLOMBIA))
        self.driver.execute_script("arguments[0].click();", prefix_option_element)
        
        self.do_send_keys(self.CONTACT_PHONE_INPUT, phone_number)
        self.do_send_keys(self.CONTACT_EMAIL_INPUT, email) 
        self.do_send_keys(self.CONTACT_CONFIRM_EMAIL_INPUT, email)
        
        logger.info("Aceptando términos.")
        
        # <<< --- INICIO CORRECCIÓN --- >>>
        # Ahora busca el locator en el archivo locators_rt.py
        terms_loc = locators_rt.get_locator("contact_terms_checkbox", self.current_url)
        terms_element = wait.until(EC.element_to_be_clickable(terms_loc))
        # <<< --- FIN CORRECCIÓN --- >>>
        
        self.driver.execute_script("arguments[0].click();", terms_element)

    def click_continue(self):
        logger.info("Haciendo clic en Continuar...")
        wait = WebDriverWait(self.driver, 20)
        
        try:
            header = self.driver.find_element(By.TAG_NAME, "header")
            self.driver.execute_script("arguments[0].style.position = 'absolute';", header)
            logger.info("Cabecera 'sticky' deshabilitada temporalmente.")
        except:
            pass 

        continue_btn = wait.until(EC.element_to_be_clickable(self.CONTINUE_BUTTON))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", continue_btn)
        
        self.driver.execute_script("arguments[0].click();", continue_btn)