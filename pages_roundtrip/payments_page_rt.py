import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages_roundtrip.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)

class PaymentsPageRT(BasePage):

    PAGE_LOADER_PAGOS = (By.CSS_SELECTOR, "div.page-loader") 
    AVIANCA_CREDITS_CHECKBOX = (By.XPATH, "/html/body/dcx-content-body/div/div/div[3]/div/div[1]/div/div[1]/dcx-component/div[1]/div[2]/payment-discount/div/div/toggle/label/span/span[1]/input")
    VOUCHER_NUMBER_INPUT = (By.ID, "number")
    VOUCHER_PIN_INPUT = (By.ID, "pin")
    INGRESAR_BTN = (By.ID, "buttonAviancaCredits")
    APLICAR_BTN = (By.XPATH, "//button[contains(@class, 'ds-btn-small') and .//span[normalize-space()='Aplicar']]")
    TERMS_CHECKBOX = (By.ID, "terms")
    CONFIRM_PAY_BTN = (By.XPATH, "//button[contains(@class, 'save-user-consent-confirmation') and .//span[normalize-space()='Confirmar y pagar']]")

    def __init__(self, driver):
        super().__init__(driver)
        logger.info("Página de Pago (PaymentsPageRT) iniciada.")

    @allure.step("Esperar que el 'page-loader' desaparezca")
    def wait_for_page_to_load(self, wait: WebDriverWait, context: str = ""):
        try:
            logger.info(f"({context}) Esperando que el spinner de Pagos desaparezca...")
            wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER_PAGOS))
            logger.info(f"({context}) Spinner de Pagos desapareció.")
        except TimeoutException as e:
            error_msg = f"El spinner de carga no desapareció ({context}). Error: {e.msg}"
            logger.error(error_msg, exc_info=True)
            allure.attach(self.driver.get_screenshot_as_png(), name=f"FALLO_SPINNER_{context}", attachment_type=allure.attachment_type.PNG)
            raise TimeoutException(error_msg)

    @allure.step("Realizar pago completo con Avianca Credits")
    def pay_with_avianca_credits(self, voucher: str, pin: str):
        wait = WebDriverWait(self.driver, 40)
        try:
            self.wait_for_page_to_load(wait, "Carga inicial")
            logger.info("Buscando el <input> de Avianca Credits (con XPath)...")
            try:
                credits_cb = wait.until(EC.presence_of_element_located(self.AVIANCA_CREDITS_CHECKBOX))
                logger.info("Elemento <input> encontrado. Forzando clic con JavaScript...")

                self.driver.execute_script("arguments[0].click();", credits_cb)
                logger.info("¡Clic forzado enviado!")

            except TimeoutException:
                logger.error("No se encontró el <input> del switch con el XPath absoluto.")
                allure.attach(self.driver.get_screenshot_as_png(), name="FALLO_XPATH_SWITCH_NO_ENCONTRADO", attachment_type=allure.attachment_type.PNG)
                raise 

            logger.info("Esperando a que aparezcan los campos de Voucher y PIN...")
            wait.until(EC.visibility_of_element_located(self.VOUCHER_NUMBER_INPUT))
            logger.info("Campos de Voucher/PIN están visibles.")

            logger.info(f"Ingresando número de voucher: {voucher}")
            self.driver.find_element(*self.VOUCHER_NUMBER_INPUT).send_keys(voucher)
            logger.info("Ingresando PIN...")
            self.driver.find_element(*self.VOUCHER_PIN_INPUT).send_keys(pin)

            logger.info("Haciendo clic en 'Ingresar'...")
            ingresar_btn = wait.until(EC.element_to_be_clickable(self.INGRESAR_BTN))
            self.driver.execute_script("arguments[0].click();", ingresar_btn)

            logger.info("Esperando a que el voucher sea validado y aparezca el botón 'Aplicar'...")
            aplicar_btn = wait.until(EC.element_to_be_clickable(self.APLICAR_BTN))

            logger.info("Haciendo clic en 'Aplicar'...")
            self.driver.execute_script("arguments[0].click();", aplicar_btn)

            self.wait_for_page_to_load(wait, "Post-Aplicar Crédito")

            logger.info("Esperando la casilla de términos y condiciones...")
            terms_cb = wait.until(EC.element_to_be_clickable(self.TERMS_CHECKBOX))
            logger.info("Aceptando términos y condiciones...")
            self.driver.execute_script("arguments[0].click();", terms_cb)

            logger.info("Haciendo clic en 'Confirmar y pagar'...")
            confirm_btn = wait.until(EC.element_to_be_clickable(self.CONFIRM_PAY_BTN))
            self.driver.execute_script("arguments[0].click();", confirm_btn)

            logger.info("Pago enviado. Esperando procesamiento final...")
            self.wait_for_page_to_load(wait, "Procesamiento Final")
            logger.info("¡Flujo de pago con Avianca Credits completado!")

        except Exception as e:
            logger.error(f"Falló el proceso de pago con Avianca Credits. Error: {e}", exc_info=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"error_payment_flow_{timestamp}.png"
            allure_name = f"FALLO_FLUJO_PAGO_{timestamp}"
            
            try:
                self.take_screenshot(screenshot_name)
                logger.info(f"Captura de pantalla guardada como: {screenshot_name}")
            except Exception as e_ss:
                logger.warning(f"No se pudo tomar screenshot con self.take_screenshot. Usando allure. {e_ss}")
                allure.attach(self.driver.get_screenshot_as_png(), name=allure_name, attachment_type=allure.attachment_type.PNG)
            
            raise e 