# pages/select_flight_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.logger import get_logger
import time

logger = get_logger()

class SelectFlightPage(BasePage):
    
    # --- LOCATORS (Actualizados con tu HTML) ---
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    PRICE_BUTTON = (By.CSS_SELECTOR, "button.journey_price_button")
    BASIC_FARE_SELECT_BUTTON = (By.XPATH, "//div[contains(@class, 'fare7')]//button[contains(@class, 'fare_button')]")
    
    # Locators para el Summary
    SUMMARY_TRIGGER = (By.CSS_SELECTOR, ".summary_trigger")
    SUMMARY_PRICE_DETAIL_BUTTON = (By.CSS_SELECTOR, "button.price-breakdown-header")
    SUMMARY_CLOSE_BUTTON = (By.CSS_SELECTOR, "button.summary_close_btn")
    
    CONTINUE_BUTTON = (By.XPATH, "//button[contains(@class, 'page_button')]")

    def __init__(self, driver):
        super().__init__(driver)

    def select_basic_fare_and_continue(self):
        wait = WebDriverWait(self.driver, 45)
        
        try:
            logger.info("Esperando a que el loader de vuelos desaparezca...")
            wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
            
            logger.info("Haciendo clic en el precio del vuelo para mostrar tarifas...")
            price_button = wait.until(EC.element_to_be_clickable(self.PRICE_BUTTON))
            self.js_click(self.PRICE_BUTTON) # Usamos JS Click para robustez
            time.sleep(1)

            logger.info("Seleccionando la tarifa 'Basic'.")
            basic_fare_button = wait.until(EC.element_to_be_clickable(self.BASIC_FARE_SELECT_BUTTON))
            self.js_click(self.BASIC_FARE_SELECT_BUTTON) # Usamos JS Click
            
            logger.info("Esperando a que el loader desaparezca después de seleccionar la tarifa...")
            wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
            
            # --- Revisión del Summary ---
            self.review_summary(wait)

            logger.info("Haciendo clic en 'Continuar' para ir a la página de pasajeros.")
            continue_button = wait.until(EC.element_to_be_clickable(self.CONTINUE_BUTTON))
            self.js_click(self.CONTINUE_BUTTON) # Usamos JS Click

        except Exception as e:
            logger.error(f"Falló durante la selección de vuelo. Error: {e}")
            self.driver.save_screenshot("error_screenshot_flight_page.png")
            raise

    def review_summary(self, wait):
        """Abre y cierra el modal del resumen de compra con un doble clic,
           manejando elementos 'stale'."""
        logger.info("Abriendo el resumen de compra (Summary) con doble clic.")
        
        # --- Primer Clic ---
        # Buscamos el elemento y hacemos el primer clic
        summary_trigger_element_1 = wait.until(EC.element_to_be_clickable(self.SUMMARY_TRIGGER))
        summary_trigger_element_1.click()
        logger.info("Primer clic en el resumen.")
        
        # Esperamos los 2 segundos que pediste
        time.sleep(2)
        
        # --- Segundo Clic ---
        # ¡VOLVEMOS A BUSCAR EL ELEMENTO! Esta es la clave.
        logger.info("Volviendo a buscar el elemento del resumen para el segundo clic.")
        summary_trigger_element_2 = wait.until(EC.element_to_be_clickable(self.SUMMARY_TRIGGER))
        summary_trigger_element_2.click()
        logger.info("Segundo clic en el resumen para asegurar la apertura.")
        time.sleep(2) # Pausa para ver el modal

        # 2. ESPERAMOS explícitamente a que el botón "Ver detalle" sea clickeable.
        #    Esta es la pieza que faltaba.
        logger.info("Esperando a que el botón 'Ver detalle' esté listo...")
        detail_button = wait.until(EC.element_to_be_clickable(self.SUMMARY_PRICE_DETAIL_BUTTON))
        # 3. Hacemos el segundo clic para expandir.
        logger.info("Expandiendo 'Ver detalle' en el resumen.")
        self.driver.execute_script("arguments[0].click();", detail_button)
        time.sleep(2) # Pausa para que veas la expansión

        # Buscamos y hacemos clic en el botón de cerrar
        logger.info("Cerrando el resumen de compra.")
        summary_close_element = wait.until(EC.element_to_be_clickable(self.SUMMARY_CLOSE_BUTTON))
        summary_close_element.click()
        time.sleep(1) # Pausa para que el modal se cierre correctamente


        