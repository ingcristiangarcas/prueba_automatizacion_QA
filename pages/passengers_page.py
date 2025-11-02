# pages/passengers_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from pages.base_page import BasePage
from utils.logger import get_logger
from faker import Faker
import time
import allure
import random


logger = get_logger()

# --- MAPA DE MESES ---
MONTH_MAP = {
    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
}

# --- FUNCIONES LOCALIZADORAS (MODIFICADAS PARA OPCIÓN 1) ---

# 1. Localizador ANCLA: Encuentra el contenedor del i-ésimo pasajero
def pax_container_locator(i): return (By.XPATH, f"(//personal-data-form-custom)[{i}]")

# 2. Localizador de Título (aún con índice, para el scroll inicial)
def pax_title_locator(i): return (By.XPATH, f"//h4[contains(@class, 'passenger_data_title')][.//span[contains(text(), 'Adulto {i}')]]")

# 3. Localizadores RELATIVOS: Buscan DENTRO del ancla.
#    (Nota: Ya no reciben 'i' y empiezan con './/')
def first_name_input_locator(): return (By.XPATH, ".//input[contains(@id, 'IdFirstName')]")
def last_name_input_locator(): return (By.XPATH, ".//input[contains(@id, 'IdLastName')]")
def gender_dropdown_locator(): return (By.XPATH, ".//button[contains(@id, 'IdPaxGender')]")
def dob_day_dropdown_locator(): return (By.XPATH, ".//button[contains(@id, 'dateDayId')]")
def dob_month_dropdown_locator(): return (By.XPATH, ".//button[contains(@id, 'dateMonthId')]")
def dob_year_dropdown_locator(): return (By.XPATH, ".//button[contains(@id, 'dateYearId')]")
def doc_type_dropdown_locator(): return (By.XPATH, ".//button[contains(@id, 'IdDocType')]")
def doc_number_input_locator(): return (By.XPATH, ".//input[contains(@id, 'IdDocNum')]")
def nationality_dropdown_locator(): return (By.XPATH, ".//button[contains(@id, 'IdDocNationality')]")
def frequent_flyer_dropdown_locator(): return (By.XPATH, ".//button[contains(@id, 'customerPrograms')]")

# 4. Localizadores GLOBALES: Se mantienen igual.
def dob_option_locator(text): return (By.XPATH, f"//button[.//span[normalize-space()='{text}']]")
def doc_type_option_locator(doc_type): return (By.XPATH, f"//button[.//span[normalize-space()=\"{doc_type}\"]]")
# --- FIN DE MODIFICACIONES ---


class PassengersPage(BasePage):

    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    GENDER_OPTION_MALE = (By.XPATH, "//button[.//span[normalize-space()='Masculino']]")
    GENDER_OPTION_FEMALE = (By.XPATH, "//button[.//span[normalize-space()='Femenino']]")
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

    # --- MÉTODOS DE AYUDA (MODIFICADOS PARA OPCIÓN 1) ---

    def _wait_and_click(self, wait, locator, scroll=True, base_element=None):
        """
        Espera a que un elemento sea clickeable y hace clic.
        Si 'base_element' se proporciona, busca dentro de él.
        """
        try:
            # Determinar el contexto de búsqueda
            search_context = base_element if base_element else self.driver
            
            # Encontrar el elemento relativo al contexto
            element = search_context.find_element(*locator)
            
            # Esperar a que ESE elemento sea clickeable
            wait.until(EC.element_to_be_clickable(element))
            
            if scroll:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
                    element
                )
            element.click()
            # --- INICIO DE MODIFICACIÓN "HUMANA" ---
            # Pausa aleatoria después del clic
            time.sleep(random.uniform(0.2, 0.4))
            # --- FIN DE MODIFICACIÓN ---
            
        except StaleElementReferenceException:
            time.sleep(0.5)
            # Reintentar búsqueda
            search_context = base_element if base_element else self.driver
            element = search_context.find_element(*locator)
            wait.until(EC.element_to_be_clickable(element))
            if scroll:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
                    element
                )
            element.click()
        except Exception as e:
            logger.error(f"Error al hacer clic en {locator} (base: {base_element}): {e}")
            self.take_screenshot(f"error_click_{locator[1]}.png")
            raise

    def _wait_and_send_keys(self, wait, locator, text, scroll=True, base_element=None):
        """
        Espera a que un elemento sea visible, limpia y escribe.
        Si 'base_element' se proporciona, busca dentro de él.
        """
        try:
            # Determinar el contexto de búsqueda
            search_context = base_element if base_element else self.driver
            
            # Encontrar el elemento relativo al contexto
            element = search_context.find_element(*locator)
            
            # Esperar a que ESE elemento sea visible
            # (EC.visibility_of ACEPTA un elemento)
            wait.until(EC.visibility_of(element)) 
            
            if scroll:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
                    element
                )
            element.clear()
            # --- INICIO DE MODIFICACIÓN "HUMANA" ---
            # Itera sobre cada letra en el texto
            for char in text:
                element.send_keys(char)
                # Pausa aleatoria entre 50 y 150 milisegundos
                time.sleep(random.uniform(0.05, 0.15))
            # --- FIN DE MODIFICACIÓN ---
        except Exception as e:
            logger.error(f"Error al enviar texto a {locator} (base: {base_element}): {e}")
            self.take_screenshot(f"error_sendkeys_{locator[1]}.png")
            raise
    
    # --- FIN DE MODIFICACIÓN DE HELPERS ---

    def _scroll_and_click_option(self, wait, list_container_query_selector, option_locator, max_scrolls=15, scroll_amount=100):
        """
        Este helper busca en listas GLOBALES (popups), por lo que
        NO necesita ser modificado. Está correcto como estaba.
        """
        for _ in range(max_scrolls):
            try:
                short_wait = WebDriverWait(self.driver, 0.5)
                option = short_wait.until(EC.element_to_be_clickable(option_locator))
                option.click()
                return  # Éxito
            except TimeoutException:
                try:
                    scroll_script = f"""
                    var container = document.querySelector('{list_container_query_selector}');
                    if (container) {{ container.scrollBy(0, {scroll_amount}); }}
                    """
                    self.driver.execute_script(scroll_script)
                    time.sleep(0.25)
                except Exception as scroll_e:
                    logger.warning(f"No se pudo hacer scroll en {list_container_query_selector}: {scroll_e}")
                    break 

        logger.error(f"No se pudo encontrar la opción {option_locator} después de {max_scrolls} scrolls.")
        raise TimeoutException(f"Elemento {option_locator} no encontrado en la lista virtualizada.")

    # --- LÓGICA DE LA PÁGINA ---

    @allure.step("Rellenar formularios de pasajeros de forma SECUENCIAL")
    def fill_all_data_and_continue(self, passengers_data: list):
        wait = WebDriverWait(self.driver, 45)
        logger.info("Esperando a que la página de pasajeros cargue completamente...")
        try:
            wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
        except TimeoutException:
            logger.warning("El loader tardó demasiado, continuando de todos modos...")

        if len(passengers_data) < 9:
            raise Exception(f"Se esperaban 9 pasajeros, pero solo hay {len(passengers_data)} datos.")

        interaction_wait = WebDriverWait(self.driver, 25)

        for i in range(1, 10):
            logger.info(f">>> Iniciando llenado de Pasajero {i}")
            self._fill_single_passenger(i, passengers_data[i - 1], interaction_wait)
            logger.info(f">>> Pasajero {i} finalizado.")

        self.fill_contact_data(passengers_data[0], interaction_wait)
        self.click_continue()


    def _fill_single_passenger(self, index, data, wait: WebDriverWait):
        """
        Método auxiliar para llenar UN solo pasajero.
        (MODIFICADO PARA OPCIÓN 1)
        """
        day, month_num, year = data['dob'].split('/')
        month_text = MONTH_MAP[month_num]

        try:
            logger.info(f"[Pax {index}] === Buscando contenedor de pasajero... ===")

            # --- ANCLA ---
            # 1. Encontrar el contenedor principal para este pasajero
            pax_container = wait.until(
                EC.visibility_of_element_located(pax_container_locator(index))
            )
            
            # 2. Hacer scroll a ESE contenedor (usando el título como referencia es más bonito)
            title_element = wait.until(EC.visibility_of_element_located(pax_title_locator(index)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", title_element)
            # --- FIN DE ANCLA ---

            # --- Nombre y Apellido ---
            # Llamamos al helper con el 'base_element' (pax_container)
            self._wait_and_send_keys(wait, first_name_input_locator(), data['first_name'], base_element=pax_container)
            self._wait_and_send_keys(wait, last_name_input_locator(), data['last_name'], base_element=pax_container)

            # --- Género ---
            # 1. Clic en el dropdown DENTRO del contenedor
            self._wait_and_click(wait, gender_dropdown_locator(), base_element=pax_container)
            
            # 2. Clic en la opción GLOBAL (sin base_element)
            if data['gender'] == 'Femenino':
                self._wait_and_click(wait, self.GENDER_OPTION_FEMALE, scroll=False)
            else:
                self._wait_and_click(wait, self.GENDER_OPTION_MALE, scroll=False)

            # --- Fecha de Nacimiento ---
            for attempt in range(3):
                try:
                    # Encontrar los botones DENTRO del contenedor
                    day_btn = pax_container.find_element(*dob_day_dropdown_locator())
                    month_btn = pax_container.find_element(*dob_month_dropdown_locator())
                    year_btn = pax_container.find_element(*dob_year_dropdown_locator())

                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", day_btn)
                    
                    # --- Día ---
                    day_btn_id = day_btn.get_attribute('id')
                    day_list_query = f"div[id='{day_btn_id}-list']"
                    day_btn.click()
                    # _scroll_and_click_option es global, lo cual es correcto
                    self._scroll_and_click_option(wait, day_list_query, dob_option_locator(day))

                    # --- Mes ---
                    month_btn_id = month_btn.get_attribute('id')
                    month_btn.click()
                    # _wait_and_click es global (sin base_element)
                    self._wait_and_click(wait, dob_option_locator(month_text), scroll=False)

                    # --- Año ---
                    year_btn_id = year_btn.get_attribute('id')
                    year_list_query = f"div[id='{year_btn_id}-list']"
                    year_btn.click()
                    self._scroll_and_click_option(wait, year_list_query, dob_option_locator(year), max_scrolls=25, scroll_amount=120)
                    
                    break
                
                except Exception as e:
                    logger.warning(f"[Pax {index}] Reintentando fecha de nacimiento... ({attempt+1}/3): {e}")
                    if attempt < 2:
                        time.sleep(1)
                    else:
                        raise

            # --- Documento ---
            self._wait_and_click(wait, doc_type_dropdown_locator(), base_element=pax_container)
            self._wait_and_click(wait, doc_type_option_locator(data['doc_type']), scroll=False) # Opción global
            self._wait_and_send_keys(wait, doc_number_input_locator(), data['doc_number'], base_element=pax_container)

            # --- Nacionalidad ---
            self._wait_and_click(wait, nationality_dropdown_locator(), base_element=pax_container)
            self._wait_and_click(wait, self.NATIONALITY_OPTION_COLOMBIA, scroll=False) # Opción global

            # --- Viajero frecuente (Opcional) ---
            try:
                short_wait = WebDriverWait(self.driver, 3)
                self._wait_and_click(short_wait, frequent_flyer_dropdown_locator(), base_element=pax_container)
                self._wait_and_click(short_wait, self.FREQ_FLYER_OPTION_NO_APLICA, scroll=False) # Opción global
            except Exception:
                logger.info(f"[Pax {index}] Campo de viajero frecuente no presente (ignorado).")

            logger.info(f"[Pax {index}] === Llenado completado con éxito ===")

        except Exception as e:
            logger.error(f"Error llenando datos del Pasajero {index}: {e}")
            self.take_screenshot(f"error_pax_{index}.png")
            raise

    def fill_contact_data(self, contact_pax_data, wait: WebDriverWait):
        """
        Rellena los datos de contacto del titular.
        Esta sección es global, NO necesita cambios.
        """
        logger.info("Rellenando datos de contacto del titular.")
        phone_number = contact_pax_data.get('phone', f"315{self.faker.random_number(digits=7, fix_len=True)}")
        email = contact_pax_data.get('email', self.faker.email())

        try:
            contact_input = wait.until(EC.visibility_of_element_located(self.CONTACT_PHONE_INPUT))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", contact_input)
        except Exception:
            logger.warning("No se pudo hacer scroll al campo de teléfono (puede estar visible).")
        
        # Todas estas llamadas usan localizadores globales (self.CONTACT_...),
        # por lo que NO se pasa 'base_element'.
        self._wait_and_click(wait, self.CONTACT_TITULAR_DROPDOWN, scroll=False)
        self._wait_and_click(wait, self.CONTACT_TITULAR_OPTION_TEST, scroll=False)
        self._wait_and_click(wait, self.CONTACT_PREFIX_DROPDOWN, scroll=False)
        self._wait_and_click(wait, self.CONTACT_PREFIX_COLOMBIA, scroll=False)
        self._wait_and_send_keys(wait, self.CONTACT_PHONE_INPUT, phone_number, scroll=False)
        self._wait_and_send_keys(wait, self.CONTACT_EMAIL_INPUT, email, scroll=False)
        self._wait_and_send_keys(wait, self.CONTACT_CONFIRM_EMAIL_INPUT, email, scroll=False)
        
        logger.info("Aceptando términos.")
        self._wait_and_click(wait, self.CONTACT_TERMS_CHECKBOX, scroll=False)

    def click_continue(self):
        """
This method is global, NO necesita cambios.
        """
        logger.info("Haciendo clic en Continuar...")
        wait = WebDriverWait(self.driver, 25)
        
        continue_btn = wait.until(EC.element_to_be_clickable(self.CONTINUE_BUTTON))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
        
        continue_btn.click()