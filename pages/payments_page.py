# pages/payments_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.logger import get_logger
from faker import Faker
import time
import allure

logger = get_logger()

class PaymentsPage(BasePage):
    
    # --- LOCATORS ---
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    
    # --- Localizadores Pago con Tarjeta (Caso 1) ---
    PAGE_TITLE_CARD = (By.XPATH, "//div[contains(text(), 'Pagar con tarjeta')]")
    CARD_HOLDER_IFRAME = (By.XPATH, "//iframe[contains(@id, 'braintree-hosted-field-cardholder')]")
    CARD_NUMBER_IFRAME = (By.XPATH, "//iframe[contains(@id, 'braintree-hosted-field-number')]")
    EXPIRATION_IFRAME = (By.XPATH, "//iframe[contains(@id, 'braintree-hosted-field-expirationDate')]")
    CVV_IFRAME = (By.XPATH, "//iframe[contains(@id, 'braintree-hosted-field-cvv')]")
    
    # Inputs DENTRO de los iframes
    CARD_HOLDER_INPUT = (By.ID, "cardholder-name")
    CARD_NUMBER_INPUT = (By.ID, "credit-card-number")
    EXPIRATION_INPUT = (By.ID, "expiration")
    CVV_INPUT = (By.ID, "cvv")
    
    # Inputs FUERA de los iframes (Facturación)
    BILLING_EMAIL_INPUT = (By.ID, "email")
    BILLING_ADDRESS_INPUT = (By.ID, "address")

    # --- Localizadores Avianca Credits (Caso 2)  ---
    AVIANCA_CREDITS_TOGGLE = (By.XPATH, "//label[contains(., 'Quiero pagar con avianca credits')]")
    CREDITS_NUMBER_INPUT = (By.XPATH, "//input[contains(@placeholder, 'Número de avianca credits')]")
    CREDITS_PIN_INPUT = (By.XPATH, "//input[@placeholder='PIN']")
    CREDITS_INGRESAR_BUTTON = (By.XPATH, "//button[.//span[normalize-space()='Ingresar']]")
    
    # --- Botón de Pago Final (Compartido) ---
    FINAL_PAY_BUTTON = (By.XPATH, "//button[contains(@class, 'page_button') and .//span[normalize-space()='Pagar']]")


    def __init__(self, driver):
        super().__init__(driver)
        # Faker se sigue usando para los datos de facturación
        self.faker = Faker('es_CO')

    # --- ORQUESTADOR PARA CASO 1 ---
    @allure.step("Caso 1: Rellenar pago con Tarjeta FAKE y continuar")
    def fill_card_payment_and_continue_caso1(self, card_info: dict, billing_pax_data: dict):
        """
        Orquestador principal para el Caso 1. Rellena el formulario de 
        tarjeta de crédito FAKE.
        
        :param card_info: Diccionario con los datos de la tarjeta fake.
        :param billing_pax_data: Datos del Pasajero 1 para email/dirección.
        """
        wait = WebDriverWait(self.driver, 45)
        logger.info("[Caso 1] Esperando a que la página de pagos (Tarjeta) cargue...")
        wait.until(EC.visibility_of_element_located(self.PAGE_TITLE_CARD))
        
        try:
            # --- Rellenar campos dentro de IFRAMES ---
            logger.info("[Caso 1] Rellenando datos de tarjeta (dentro de iframes)...")
            
            # Titular
            wait.until(EC.frame_to_be_available_and_switch_to_it(self.CARD_HOLDER_IFRAME))
            self.do_send_keys(self.CARD_HOLDER_INPUT, card_info['card_holder'])
            self.driver.switch_to.default_content()

            # Número de Tarjeta (¡Usando el N° FAKE, no faker!)
            wait.until(EC.frame_to_be_available_and_switch_to_it(self.CARD_NUMBER_IFRAME))
            self.do_send_keys(self.CARD_NUMBER_INPUT, card_info['card_number'])
            self.driver.switch_to.default_content()

            # Expiración
            wait.until(EC.frame_to_be_available_and_switch_to_it(self.EXPIRATION_IFRAME))
            expiration_date = f"{card_info['expiry_month']}{card_info['expiry_year'][-2:]}" # Formato MMYY
            self.do_send_keys(self.EXPIRATION_INPUT, expiration_date)
            self.driver.switch_to.default_content()

            # CVV
            wait.until(EC.frame_to_be_available_and_switch_to_it(self.CVV_IFRAME))
            self.do_send_keys(self.CVV_INPUT, card_info['cvv'])
            self.driver.switch_to.default_content()
            
            logger.info("[Caso 1] Datos de tarjeta completados.")
            
            # --- Rellenar datos de Facturación ---
            self._fill_billing_details(billing_pax_data)

            # --- Clic final en Pagar ---
            # El requisito dice "No importa que el pago sea rechazado"
            self.click_final_pay_button()
            logger.info("[Caso 1] Clic en 'Pagar' realizado. Esperando respuesta...")
            # (El test manejará la redirección o el fallo)
            
        except Exception as e:
            logger.error(f"[Caso 1] Falló durante el llenado del formulario de pago: {e}")
            self.driver.switch_to.default_content() # Asegurarse de salir del iframe si falla
            self.take_screenshot("error_pago_tarjeta.png")
            raise

    # --- ORQUESTADOR PARA CASO 2 ---
    @allure.step("Caso 2: Pagar con Avianca Credits (Voucher/PIN)")
    def fill_avianca_credits_and_continue_caso2(self, voucher: str, pin: str):
        """
        Orquestador principal para el Caso 2. Paga con Avianca Credits.
        
        :param voucher: Número de voucher [cite: 76]
        :param pin: Número de PIN [cite: 78]
        """
        wait = WebDriverWait(self.driver, 45)
        logger.info("[Caso 2] Esperando a que la página de pagos cargue...")
        try: wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
        except: pass
        
        try:
            logger.info("[Caso 2] Activando el toggle 'Quiero pagar con avianca credits'...")
            wait.until(EC.element_to_be_clickable(self.AVIANCA_CREDITS_TOGGLE))
            self.js_click(self.AVIANCA_CREDITS_TOGGLE)
            
            logger.info("[Caso 2] Rellenando datos de Avianca Credits...")
            # Esperar a que el formulario sea visible
            wait.until(EC.visibility_of_element_located(self.CREDITS_NUMBER_INPUT))
            
            self.do_send_keys(self.CREDITS_NUMBER_INPUT, voucher)
            self.do_send_keys(self.CREDITS_PIN_INPUT, pin)
            
            logger.info("[Caso 2] Haciendo clic en 'Ingresar' créditos...")
            self.js_click(self.CREDITS_INGRESAR_BUTTON)
            
            # Esperar a que el crédito se aplique
            # (Esperamos a que el botón 'Ingresar' desaparezca o se deshabilite)
            wait.until(EC.invisibility_of_element_located(self.CREDITS_INGRESAR_BUTTON))
            logger.info("[Caso 2] Créditos aplicados exitosamente.")
            
            # (En un flujo real, aquí rellenaríamos el resto del pago si el 
            # voucher no cubre todo, pero para la prueba asumimos que sí)

            # --- Clic final en Pagar ---
            self.click_final_pay_button()
            logger.info("[Caso 2] Clic en 'Pagar' realizado.")
            
        except Exception as e:
            logger.error(f"[Caso 2] Falló durante el pago con Avianca Credits: {e}")
            self.take_screenshot("error_pago_credits.png")
            raise

    # --- Métodos de Ayuda Compartidos ---
    
    def _fill_billing_details(self, billing_pax_data: dict):
        """Rellena los datos de facturación (Email, Dirección)"""
        logger.info("Rellenando datos de facturación (Email/Dirección)...")
        try:
            email = billing_pax_data.get('email', self.faker.email())
            address = self.faker.address().replace('\n', ', ') # Dirección fake
            
            self.do_send_keys(self.BILLING_EMAIL_INPUT, email)
            self.do_send_keys(self.BILLING_ADDRESS_INPUT, address)
            
            logger.info("Datos de facturación completados.")
        except Exception as e:
            logger.warning(f"No se pudieron rellenar los datos de facturación: {e}")

    def click_final_pay_button(self):
        """Scroll y clic en el botón final de 'Pagar'."""
        logger.info("Buscando el botón final 'Pagar'...")
        wait = WebDriverWait(self.driver, 20)
        
        pay_btn = wait.until(EC.presence_of_element_located(self.FINAL_PAY_BUTTON))
        
        self.driver.execute_script("arguments[0].scrollIntoView(true);", pay_btn)
        time.sleep(1) 
        
        self.driver.execute_script("arguments[0].click();", pay_btn)
        logger.info("Clic forzado en 'Pagar' realizado.")