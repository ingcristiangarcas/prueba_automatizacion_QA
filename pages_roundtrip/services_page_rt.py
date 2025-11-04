import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from pages_roundtrip.base_page import BasePage
from utils.logger import get_logger

logger = get_logger()

class ServicesPageRT(BasePage):
    # --- Locators Principales de la Página ---
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    ADD_NORMAL_BAGGAGE_BTN = (By.ID, "serviceButtonTypeBaggage")
    ADD_SPORTS_BAGGAGE_BTN = (By.ID, "serviceButtonTypeOversize")
    CONTINUE_BTN = (By.XPATH, "//button[contains(@class, 'page_button') and .//span[normalize-space()='Continuar']]")
    
    # --- Locators del Modal de Equipaje (Dinámico) ---
    PLUS_BUTTONS_MODAL = (By.CSS_SELECTOR, "button.ui-num-ud_button.plus")
    CONFIRM_MODAL_BTN = (By.XPATH, "//button[contains(@class, 'btn-action') and .//span[normalize-space()='Confirmar']]")

    # --- Locators del Resumen de Compra (Basket) ---
    SUMMARY_TRIGGER_BTN = (By.CSS_SELECTOR, "button.summary_trigger")
    SUMMARY_VER_DETALLE_BTN = (By.CSS_SELECTOR, "button.price-breakdown-header")
    SUMMARY_BASKET_CONTENT = (By.ID, "summaryTypologyPerBookingId")
    SUMMARY_CERRAR_BTN = (By.CSS_SELECTOR, "button.summary_close_btn")


    def __init__(self, driver):
        super().__init__(driver)
        logger.info("Página de Servicios (ServicesPageRT) iniciada.")

    @allure.step("Esperar a que cargue la página de Servicios")
    def wait_for_page_to_load(self):
        wait = WebDriverWait(self.driver, 40)
        try:
            wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
            logger.info("Page loader de Servicios desapareció.")
        except TimeoutException:
            logger.warning("El 'page loader' de Servicios no desapareció. Continuando...")
        
        try:
            wait.until(EC.element_to_be_clickable(self.ADD_NORMAL_BAGGAGE_BTN))
            logger.info("Página de Servicios cargada y lista.")
        except TimeoutException as e:
            logger.error(f"La página de Servicios no cargó los botones de equipaje: {e}")
            self.take_screenshot("error_services_load.png")
            raise

    @allure.step("Añadir todos los servicios de equipaje (Normal y Deportivo)")
    def add_all_baggage_services(self):
        wait = WebDriverWait(self.driver, 15)
        
        logger.info("Iniciando adición de Equipaje Normal...")
        self._add_baggage_generic(self.ADD_NORMAL_BAGGAGE_BTN, wait)
        
        logger.info("Pausa de 1 segundo antes de añadir equipaje deportivo.")
        time.sleep(3)
        
        
        logger.info("Todos los servicios de equipaje han sido añadidos.")

    def _add_baggage_generic(self, add_button_locator, wait: WebDriverWait):
        try:
            add_btn = wait.until(EC.element_to_be_clickable(add_button_locator))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", add_btn)
            time.sleep(0.5) 
            add_btn.click()
            
            logger.info("Modal abierto. Buscando botones '+'...")
            plus_buttons = wait.until(EC.presence_of_all_elements_located(self.PLUS_BUTTONS_MODAL))
            
            logger.info(f"Encontrados {len(plus_buttons)} botones '+' (uno por pasajero).")
            
            for i, button in enumerate(plus_buttons, start=1):
                try:
                    button.click()
                    logger.info(f"Clic en '+' del pasajero {i}/{len(plus_buttons)}")
                    time.sleep(0.5) 
                except Exception as e:
                    logger.warning(f"No se pudo hacer clic en el botón '+' {i}. Error: {e}")
            
            logger.info("Pausa de 1.5s para esperar que el servidor procese y habilite 'Confirmar'.")
            time.sleep(1.5)

            logger.info("Buscando y haciendo scroll al botón 'Confirmar' en el modal.")
            confirm_btn_element = wait.until(EC.presence_of_element_located(self.CONFIRM_MODAL_BTN))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", confirm_btn_element)
            
            wait.until(EC.element_to_be_clickable(self.CONFIRM_MODAL_BTN))
            self.driver.execute_script("arguments[0].click();", confirm_btn_element) 

            wait.until(EC.invisibility_of_element_located(self.CONFIRM_MODAL_BTN))
            logger.info("Modal de equipaje cerrado.")

        except Exception as e:
            locator_str = add_button_locator[1] 
            logger.error(f"Falló el proceso de añadir equipaje para '{locator_str}'. Error: {e}")
            self.take_screenshot(f"error_adding_baggage_{locator_str}.png")
            raise

    @allure.step("Validar servicios en el resumen de compra (basket) [Plan B]")
    def validate_services_in_basket(self):
        """
        [Plan B] Abre el resumen, hace SCROLL al detalle, lo abre,
        espera 2s, y cierra.
        """
        wait = WebDriverWait(self.driver, 30)
        try:
           
            # 1. Abrir el Summary
            logger.info("Esperando que el gatillo del summary sea clickeable...")
            wait.until(EC.element_to_be_clickable(self.SUMMARY_TRIGGER_BTN))
            self.js_click(self.SUMMARY_TRIGGER_BTN) 
            time.sleep(1.0)

            # 2. Clic en "Ver detalle"
            logger.info("Haciendo clic en 'Ver detalle'...")
            wait.until(EC.element_to_be_clickable(self.SUMMARY_VER_DETALLE_BTN))
            self.js_click(self.SUMMARY_VER_DETALLE_BTN)
            time.sleep(1.5)

            # 3. Validar (Aserción)
            logger.info("Esperando que el contenido del basket sea visible...")
            basket_element = wait.until(EC.visibility_of_element_located(self.SUMMARY_BASKET_CONTENT))
            basket_text = basket_element.text
            logger.info("Validación visual del summary (clics exitosos).")
            allure.attach(f"Texto del Summary: {basket_text}", name="Validación del Summary", attachment_type=allure.attachment_type.TEXT)

            # 4. Cerrar el Summary
            logger.info("Cerrando el resumen de compra.")
            close_button = wait.until(EC.element_to_be_clickable(self.SUMMARY_CERRAR_BTN))
            self.js_click(self.SUMMARY_CERRAR_BTN)
            time.sleep(1.5)

        except AssertionError as e:
            logger.error(f"FALLO DE ASERCIÓN en Summary: {e}")
            self.take_screenshot("error_screenshot_summary_validation.png")
            raise    
        except Exception as e:
            logger.error(f"[Plan B] No se pudo validar el basket. Error: {e}")
            self.take_screenshot("error_basket_validation_plan_b.png")
            raise

    @allure.step("Hacer clic en 'Continuar' a Pasajeros")
    def click_continue(self):
        wait = WebDriverWait(self.driver, 30)
        try:
            logger.info("Haciendo clic en 'Continuar' para ir a la página de pasajeros.")
            continue_button = wait.until(EC.element_to_be_clickable(self.CONTINUE_BTN))
            try:
                 continue_button.click()
            except ElementClickInterceptedException:
                 logger.warning("Clic normal interceptado en Continuar, intentando JS.")
                 self.js_click(self.CONTINUE_BTN)
        except Exception as e:
            logger.error(f"Falló al hacer clic en 'Continuar' a Pasajeros. Error: {e}")
            self.take_screenshot("error_clic_continuar_pax.png")
            raise    