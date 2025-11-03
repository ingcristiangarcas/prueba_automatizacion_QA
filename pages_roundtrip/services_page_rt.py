import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger()

class ServicesPageRT(BasePage):
    """
    Página de Servicios (Ancillaries) para RoundTrip.
    Cumple los requisitos del Caso 2:
    - Añadir equipaje normal para todos los pasajeros.
    - Añadir equipaje deportivo para todos los pasajeros.
    - Validar en el basket (resumen de compra).
    """

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
    SUMMARY_CERRAR_BTN = (By.XPATH, "//button[.//span[normalize-space()='Cerrar']]")


    def __init__(self, driver):
        super().__init__(driver)
        logger.info("Página de Servicios (ServicesPageRT) iniciada.")

    @allure.step("Esperar a que cargue la página de Servicios")
    def wait_for_page_to_load(self):
        """Espera a que el loader desaparezca y los botones de añadir estén listos."""
        wait = WebDriverWait(self.driver, 20)
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
        """
        Método principal que añade equipaje normal y deportivo a TODOS los pasajeros.
        """
        wait = WebDriverWait(self.driver, 10)
        
        # --- 1. Equipaje Normal (Carry-on y Bodega) ---
        logger.info("Iniciando adición de Equipaje Normal...")
        self._add_baggage_generic(self.ADD_NORMAL_BAGGAGE_BTN, wait)
        
        logger.info("Pausa de 1 segundo antes de añadir equipaje deportivo.")
        time.sleep(1.0)
        
        # --- 2. Equipaje Deportivo ---
        logger.info("Iniciando adición de Equipaje Deportivo...")
        self._add_baggage_generic(self.ADD_SPORTS_BAGGAGE_BTN, wait)
        
        logger.info("Todos los servicios de equipaje han sido añadidos.")

    def _add_baggage_generic(self, add_button_locator, wait: WebDriverWait):
        """
        Lógica genérica para:
        1. Clic "Añadir" (Equipaje Normal o Deportivo).
        2. Clic en TODOS los botones "+" (uno por pasajero).
        3. Clic en "Confirmar".
        """
        try:
            # 1. Hacer scroll y clic en "Añadir"
            add_btn = wait.until(EC.element_to_be_clickable(add_button_locator))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", add_btn)
            time.sleep(0.5) 
            add_btn.click()
            
            # 2. Esperar a que el modal cargue y encontrar TODOS los botones "+"
            logger.info("Modal abierto. Buscando botones '+'...")
            plus_buttons = wait.until(EC.presence_of_all_elements_located(self.PLUS_BUTTONS_MODAL))
            
            logger.info(f"Encontrados {len(plus_buttons)} botones '+' (uno por pasajero).")
            
            # 3. Hacer clic en cada botón "+" lentamente
            for i, button in enumerate(plus_buttons, start=1):
                try:
                    button.click()
                    logger.info(f"Clic en '+' del pasajero {i}/{len(plus_buttons)}")
                    time.sleep(0.5) # Pausa "humana"
                except Exception as e:
                    logger.warning(f"No se pudo hacer clic en el botón '+' {i}. Error: {e}")
            
            # <<< --- INICIO DE CORRECCIÓN (v6) --- >>>
            logger.info("Pausa de 1.5s para esperar que el servidor procese y habilite 'Confirmar'.")
            time.sleep(1.5) # Pausa fija para que el JS del sitio recalcule

            # 4. Hacer scroll y clic en "Confirmar"
            logger.info("Buscando y haciendo scroll al botón 'Confirmar' en el modal.")
            
            # Primero, encontramos el elemento (no esperamos que sea clicable todavía)
            confirm_btn_element = wait.until(EC.presence_of_element_located(self.CONFIRM_MODAL_BTN))
            
            # Hacemos el scroll que pediste
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", confirm_btn_element)
            
            # Ahora SÍ esperamos a que sea CLICABLE (después de la pausa y el scroll)
            wait.until(EC.element_to_be_clickable(self.CONFIRM_MODAL_BTN))
            self.driver.execute_script("arguments[0].click();", confirm_btn_element) # Clic con JS
            # <<< --- FIN DE CORRECCIÓN (v6) --- >>>
            
            # 5. Esperar a que el modal se cierre
            wait.until(EC.invisibility_of_element_located(self.CONFIRM_MODAL_BTN))
            logger.info("Modal de equipaje cerrado.")

        except Exception as e:
            locator_str = add_button_locator[1] 
            logger.error(f"Falló el proceso de añadir equipaje para '{locator_str}'. Error: {e}")
            self.take_screenshot(f"error_adding_baggage_{locator_str}.png")
            raise

    @allure.step("Validar servicios en el resumen de compra (basket)")
    def validate_services_in_basket(self):
        """
        Abre el resumen de compra (basket), muestra el detalle y toma screenshot.
        """
        wait = WebDriverWait(self.driver, 10)
        try:
            logger.info("Abriendo resumen de compra (basket)...")
            summary_btn = wait.until(EC.element_to_be_clickable(self.SUMMARY_TRIGGER_BTN))
            summary_btn.click()
            time.sleep(0.5)
            
            logger.info("Abriendo 'Ver detalle'...")
            detail_btn = wait.until(EC.element_to_be_clickable(self.SUMMARY_VER_DETALLE_BTN))
            detail_btn.click()
            time.sleep(1.0) 
            
            allure.attach(self.driver.get_screenshot_as_png(), name="Detalle_Basket_Servicios", attachment_type=allure.attachment_type.PNG)
            logger.info("Captura de pantalla del detalle del basket tomada.")
            
            logger.info("Cerrando resumen de compra...")
            close_btn = wait.until(EC.element_to_be_clickable(self.SUMMARY_CERRAR_BTN))
            close_btn.click()
            wait.until(EC.invisibility_of_element_located(self.SUMMARY_CERRAR_BTN))
            
        except Exception as e:
            logger.error(f"No se pudo validar el basket. Error: {e}")
            self.take_screenshot("error_basket_validation.png")
            raise

    @allure.step("Continuar a la página de Seatmap")
    def click_continue(self):
        """
        Hace clic en el botón 'Continuar' al final de la página.
        """
        logger.info("Haciendo clic en 'Continuar'...")
        try:
            continue_btn = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(self.CONTINUE_BTN))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", continue_btn)
            time.sleep(0.5) 
            self.driver.execute_script("arguments[0].click();", continue_btn)
        except Exception as e:
            logger.error(f"No se pudo hacer clic en 'Continuar' en Servicios. Error: {e}")
            self.take_screenshot("error_continue_services.png")
            raise