# pages/passengers_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pages.base_page import BasePage
from utils.logger import get_logger
from faker import Faker
import time

logger = get_logger()

class PassengersPage(BasePage):
    
    # --- LOCATORS ---
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    FIRST_NAME_INPUT = (By.XPATH, "//input[contains(@id, 'IdFirstName')]")
    LAST_NAME_INPUT = (By.XPATH, "//input[contains(@id, 'IdLastName')]")
    
    # Género
    GENDER_DROPDOWN = (By.XPATH, "//button[contains(@id, 'IdPaxGender')]")
    GENDER_OPTION_MALE = (By.XPATH, "//button[.//span[normalize-space()='Masculino']]")
    
    # Fecha de Nacimiento
    DOB_DAY_DROPDOWN = (By.XPATH, "//button[contains(@id, 'dateDayId')]")
    DOB_MONTH_DROPDOWN = (By.XPATH, "//button[contains(@id, 'dateMonthId')]")
    DOB_YEAR_DROPDOWN = (By.XPATH, "//button[contains(@id, 'dateYearId')]")

    # Nacionalidad
    NATIONALITY_DROPDOWN = (By.XPATH, "//button[contains(@id, 'IdDocNationality')]")
    NATIONALITY_OPTION_COLOMBIA = (By.XPATH, "//button[.//span[normalize-space()='Colombia']]")

  
    CONTACT_PREFIX_DROPDOWN = (By.ID, "phone_prefixPhoneId")
    CONTACT_PREFIX_COLOMBIA = (By.XPATH, "//button[contains(@id, 'phone_prefixPhoneId') and .//span[text()='Colombia']]")
    CONTACT_PHONE_INPUT = (By.ID, "phone_phoneNumberId")
    CONTACT_EMAIL_INPUT = (By.ID, "email")
    CONTACT_CONFIRM_EMAIL_INPUT = (By.ID, "confirmEmail")

    CONTACT_TERMS_LABEL = (By.XPATH, "//label[@for='sendNewsLetter']")
    CONTINUE_BUTTON = (By.XPATH, "//button[contains(@class, 'page_button') and .//span[normalize-space()='Continuar']]")


    def __init__(self, driver):
        super().__init__(driver)
        self.faker = Faker('es_ES')

    def fill_all_data_and_continue(self, num_adults=1):
        """Método principal que rellena pasajeros, contacto y continúa."""
        self.fill_passengers_data(num_adults)
        self.fill_contact_data()
        self.click_continue()
        
    def fill_passengers_data(self, num_adults=1):
        wait = WebDriverWait(self.driver, 30)
        logger.info("Esperando a que la página de pasajeros cargue...")
        try: wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
        except: pass
        wait.until(EC.visibility_of_element_located(self.FIRST_NAME_INPUT))
        
        if num_adults > 0:
            # --- Rellenar Datos del Pasajero 1 ---
            first_name, last_name = self.faker.first_name_male(), self.faker.last_name()
            birth_year, birth_month_text, birth_day = "1990", "Octubre", "15"
            
            logger.info(f"Rellenando datos del Pasajero 1: {first_name} {last_name}")
            self.do_send_keys(self.FIRST_NAME_INPUT, first_name)
            self.do_send_keys(self.LAST_NAME_INPUT, last_name)
            self.do_click(self.GENDER_DROPDOWN); time.sleep(0.5)
            self.do_click(self.GENDER_OPTION_MALE)
            
            self.do_click(self.DOB_DAY_DROPDOWN); time.sleep(0.5)
            self.do_click((By.XPATH, f"//button[.//span[normalize-space()='{birth_day}']]"))
            self.do_click(self.DOB_MONTH_DROPDOWN); time.sleep(0.5)
            self.do_click((By.XPATH, f"//button[.//span[normalize-space()='{birth_month_text}']]"))
            self.do_click(self.DOB_YEAR_DROPDOWN); time.sleep(0.5)
            self.do_click((By.XPATH, f"//button[.//span[normalize-space()='{birth_year}']]"))
            
            self.do_click(self.NATIONALITY_DROPDOWN); time.sleep(0.5)
            self.do_click(self.NATIONALITY_OPTION_COLOMBIA)
            
    def fill_contact_data(self):
        """Rellena la sección de datos de contacto del titular."""
        logger.info("Rellenando datos de contacto del titular.")
        
        phone_number = f"315{self.faker.random_number(digits=7, fix_len=True)}"
        email = self.faker.email()
        
        # Scroll para asegurar que la sección de contacto esté visible
        self.driver.execute_script("arguments[0].scrollIntoView(true);", self.driver.find_element(*self.CONTACT_PHONE_INPUT))
        time.sleep(1)

        # Rellenar el formulario
        self.do_click(self.CONTACT_PREFIX_DROPDOWN)
        time.sleep(0.5)
        self.do_click(self.CONTACT_PREFIX_COLOMBIA)
        
        self.do_send_keys(self.CONTACT_PHONE_INPUT, phone_number)
        self.do_send_keys(self.CONTACT_EMAIL_INPUT, email)
        self.do_send_keys(self.CONTACT_CONFIRM_EMAIL_INPUT, email)
        
        # Aceptar términos haciendo clic en la etiqueta (label)
        self.do_click(self.CONTACT_TERMS_LABEL)
        time.sleep(1)

    def click_continue(self):
        """Usa un clic forzado con JavaScript para máxima robustez."""
        logger.info("Haciendo clic en Continuar para ir a la página de servicios con JS Force Click.")
        wait = WebDriverWait(self.driver, 20)
        
        continue_btn = wait.until(EC.presence_of_element_located(self.CONTINUE_BUTTON))
        
        self.driver.execute_script("arguments[0].scrollIntoView(true);", continue_btn)
        time.sleep(1) 
        
        self.driver.execute_script("arguments[0].click();", continue_btn)
        
        logger.info("Clic forzado en 'Continuar' realizado.")