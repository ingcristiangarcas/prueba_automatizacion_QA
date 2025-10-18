# pages/payments_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.logger import get_logger
from faker import Faker
import time


logger = get_logger()

class PaymentsPage(BasePage):
    
    
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    PAGE_TITLE = (By.XPATH, "//div[contains(text(), 'Pagar con tarjeta')]")

    
    CARD_HOLDER_IFRAME = (By.XPATH, "//iframe[contains(@id, 'braintree-hosted-field-cardholder')]")
    CARD_NUMBER_IFRAME = (By.XPATH, "//iframe[contains(@id, 'braintree-hosted-field-number')]")
    EXPIRATION_IFRAME = (By.XPATH, "//iframe[contains(@id, 'braintree-hosted-field-expirationDate')]")
    CVV_IFRAME = (By.XPATH, "//iframe[contains(@id, 'braintree-hosted-field-cvv')]")
    
    
    CARD_HOLDER_INPUT = (By.ID, "cardholder-name")
    CARD_NUMBER_INPUT = (By.ID, "credit-card-number")
    EXPIRATION_INPUT = (By.ID, "expiration")
    CVV_INPUT = (By.ID, "cvv")
    
    
    BILLING_EMAIL_INPUT = (By.ID, "email")
    BILLING_ADDRESS_INPUT = (By.ID, "address")
    

    def __init__(self, driver):
        super().__init__(driver)
        self.faker = Faker()

    def fill_payment_form_and_pay(self):
        wait = WebDriverWait(self.driver, 45)
        logger.info("Esperando a que la página de pagos cargue...")
        wait.until(EC.visibility_of_element_located(self.PAGE_TITLE))
        
        self._fill_card_holder(wait)
        self._fill_card_number(wait)
        self._fill_expiration_date(wait)
        self._fill_cvv(wait)
        self._fill_billing_details(wait)
        
    
   
    def _fill_card_holder(self, wait):
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it(self.CARD_HOLDER_IFRAME))
            self.do_send_keys(self.CARD_HOLDER_INPUT, self.faker.name())
        finally:
            self.driver.switch_to.default_content()

    def _fill_card_number(self, wait):
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it(self.CARD_NUMBER_IFRAME))
            self.do_send_keys(self.CARD_NUMBER_INPUT, self.faker.credit_card_number())
        finally:
            self.driver.switch_to.default_content()

    def fill_card_holder_name(self):
        """Espera, entra al iframe y rellena solo el nombre del titular."""
        wait = WebDriverWait(self.driver, 60)
        
        logger.info("Esperando a que el iframe de pago esté disponible...")
        wait.until(EC.frame_to_be_available_and_switch_to_it(self.PAYMENT_IFRAME))
        
        logger.info("Dentro del iframe. Rellenando el nombre del titular...")
        try:
            
            wait.until(EC.visibility_of_element_located(self.CARD_HOLDER_INPUT))
            card_holder = self.faker.name()
            self.do_send_keys(self.CARD_HOLDER_INPUT, card_holder)
        
        finally:
            self.driver.switch_to.default_content()
            logger.info("Se ha salido del iframe de pago.")
        
        time.sleep(3)