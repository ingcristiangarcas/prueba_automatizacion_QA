# pages/base_page.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.logger import get_logger
import time
import allure
import os      
from faker import Faker

logger = get_logger()

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.faker = Faker()

    def do_click(self, by_locator, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(by_locator)).click()
        except TimeoutException:
            logger.error(f"Error: Elemento REQUERIDO no encontrado o no clickeable con el locator {by_locator}")
            raise

    def click_if_present(self, by_locator, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(by_locator)).click()
            logger.info(f"Elemento opcional encontrado y clickeado: {by_locator}")
        except TimeoutException:
            logger.info(f"Elemento opcional no encontrado, continuando ejecución: {by_locator}")
            pass

    def do_send_keys(self, by_locator, text, timeout=15):
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(by_locator))
            element.clear()
            element.send_keys(text)
        except TimeoutException:
            logger.error(f"Error: Elemento REQUERIDO no encontrado con el locator {by_locator}")
            raise

    def send_keys_slowly(self, by_locator, text, timeout=15):
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(by_locator))
            element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(0.25) 
        except TimeoutException:
            logger.error(f"Error: Elemento REQUERIDO no encontrado para escritura lenta: {by_locator}")
            raise
            
    def get_element_text(self, by_locator, timeout=15):
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(by_locator))
            return element.text
        except TimeoutException:
            logger.error(f"Error: Elemento REQUERIDO no encontrado con el locator {by_locator}")
            raise

    def js_click(self, by_locator, timeout=20):
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(by_locator))
            self.driver.execute_script("arguments[0].click();", element)
            logger.info(f"Clic con JS en el elemento: {by_locator}")
        except TimeoutException:
            logger.error(f"Error: Elemento REQUERIDO no encontrado para clic con JS: {by_locator}")
            raise
    
    def wait_for_element_to_be_clickable(self, by_locator, timeout=15):
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(by_locator))
            logger.info(f"Elemento {by_locator} está listo y es clickeable.")
        except TimeoutException:
            logger.error(f"Error: El elemento {by_locator} no se volvió clickeable en el tiempo esperado.")
            raise
        
    def take_screenshot(self, name):
        """
        Toma una captura de pantalla, la guarda localmente 
        y la adjunta al reporte de Allure.
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{name}_{timestamp}.png"
        
        ss_dir = os.path.join(os.path.dirname(__file__), '..', 'screenshots')
        os.makedirs(ss_dir, exist_ok=True)
        file_path = os.path.join(ss_dir, filename)

        try:
            png_data = self.driver.get_screenshot_as_png()
            
            with open(file_path, 'wb') as f:
                f.write(png_data)
            
            allure.attach(
                png_data,
                name=name,
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"Captura de pantalla guardada en: {file_path}")
            logger.info(f"Captura de pantalla '{name}' adjuntada a Allure.")
        
        except Exception as e:
            logger.error(f"No se pudo tomar la captura de pantalla: {e}")