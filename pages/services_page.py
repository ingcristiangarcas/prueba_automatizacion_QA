# pages/services_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.logger import get_logger
import time

logger = get_logger()

class ServicesPage(BasePage):
    
    # --- LOCATORS ---
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    SERVICE_CARDS = (By.XPATH, "//card-component")
    
    # --- Locators DENTRO de los modales (los buscaremos todos) ---
    MODAL_ADD_PLUS_BUTTONS = (By.XPATH, "//div[contains(@class, 'modal-service_selector')]//button[contains(@class, 'ui-num-ud_button plus')]")
    MODAL_ADD_LABEL_BUTTON = (By.XPATH, "//div[contains(@class, 'modal-service_selector')]//label[contains(@class, 'service_item_button')]")
    MODAL_TERMS_CHECKBOX = (By.ID, "termsconditions")
    MODAL_CONFIRM_BUTTON = (By.XPATH, "//div[contains(@class, 'modal-service_selector')]//button[.//span[normalize-space()='Confirmar']]")
    MODAL_CONTINUE_BUTTON = (By.XPATH, "//div[contains(@class, 'modal-service_selector')]//button[.//span[normalize-space()='Continuar']]")
    
    # --- Locators del Basket/Summary ---
    BASKET_SUMMARY_TRIGGER = (By.CSS_SELECTOR, ".summary_trigger")
    BASKET_DETAIL_BUTTON = (By.CSS_SELECTOR, "button.price-breakdown-header")
    BASKET_CLOSE_BUTTON = (By.CSS_SELECTOR, "button.summary_close_btn")

    CONTINUE_BUTTON = (By.CSS_SELECTOR, "div.page-actions button.btn-action")

    def __init__(self, driver):
        super().__init__(driver)

    def add_all_services_and_validate_basket(self):
        self.add_all_available_services()
        self.review_basket()
        self.click_continue()

    def add_all_available_services(self):
        wait = WebDriverWait(self.driver, 25)
        logger.info("Esperando a que la página de servicios cargue...")
        try: wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
        except: pass
        wait.until(EC.presence_of_all_elements_located(self.SERVICE_CARDS))
        
        num_service_cards = len(self.driver.find_elements(*self.SERVICE_CARDS))
        logger.info(f"Se encontraron {num_service_cards} tarjetas de servicio.")
        
        for i in range(num_service_cards):
            all_cards = wait.until(EC.presence_of_all_elements_located(self.SERVICE_CARDS))
            current_card = all_cards[i]
            title_text = current_card.find_element(By.XPATH, ".//div[contains(@class, 'services-card_title')]").text
            
            # Saltamos la tarjeta de "Asistencia especial" que solo tiene "Continuar"
            if "Asistencia especial" in title_text:
                logger.info(f"Omitiendo servicio '{title_text}' según la lógica.")
                continue

            logger.info(f"Procesando servicio: '{title_text}'...")
            
            try:
                add_button = current_card.find_element(By.XPATH, ".//button[contains(@class, 'services-card_action_button')]")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
                time.sleep(2.5)
                self.driver.execute_script("arguments[0].click();", add_button)
                time.sleep(3)

                # --- LÓGICA OPORTUNISTA ---
                # Busca y clickea botones '+' SI EXISTEN
                plus_buttons = self.driver.find_elements(*self.MODAL_ADD_PLUS_BUTTONS)
                if plus_buttons:
                    logger.info(f"Encontrados {len(plus_buttons)} botones '+' para '{title_text}'.")
                    for btn in plus_buttons: self.js_click_element(btn)
                
                # Busca y clickea botones 'Añadir' (label) SI EXISTEN
                label_buttons = self.driver.find_elements(*self.MODAL_ADD_LABEL_BUTTON)
                if label_buttons:
                    logger.info(f"Encontrado botón 'Añadir' (label) para '{title_text}'.")
                    self.js_click_element(label_buttons[0])
                
                # Busca y clickea el checkbox de términos SI EXISTE
                terms_checkbox = self.driver.find_elements(*self.MODAL_TERMS_CHECKBOX)
                if terms_checkbox:
                    logger.info(f"Encontrado checkbox de términos para '{title_text}'.")
                    self.js_click_element(terms_checkbox[0])

                # Cierra el modal con "Confirmar" si existe
                confirm_buttons = self.driver.find_elements(*self.MODAL_CONFIRM_BUTTON)
                if confirm_buttons:
                    logger.info(f"Confirmando servicio '{title_text}'.")
                    self.js_click_element(confirm_buttons[0])
                
                time.sleep(4) # Pausa larga para que la página se estabilice

            except Exception as e:
                logger.error(f"Error procesando el servicio '{title_text}': {e}")
    
    def review_basket(self):
        """Abre, expande detalles y cierra el basket/summary."""
        wait = WebDriverWait(self.driver, 20)
        logger.info("Validando el basket de compra...")
        
        try:
            # Hacemos scroll hasta el final para asegurar que el trigger esté visible
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)

            logger.info("Abriendo el resumen de compra (Summary).")
            summary_trigger = wait.until(EC.element_to_be_clickable(self.BASKET_SUMMARY_TRIGGER))
            self.driver.execute_script("arguments[0].click();", summary_trigger)
            time.sleep(4)
            
            logger.info("Expandiendo 'Ver detalle' en el resumen.")
            detail_button = wait.until(EC.element_to_be_clickable(self.BASKET_DETAIL_BUTTON))
            self.driver.execute_script("arguments[0].click();", detail_button)
            time.sleep(4)
            
            logger.info("Cerrando el resumen de compra.")
            close_button = wait.until(EC.element_to_be_clickable(self.BASKET_CLOSE_BUTTON))
            self.driver.execute_script("arguments[0].click();", close_button)
            time.sleep(4)
            logger.info("Basket validado con éxito.")
        except Exception as e:
            logger.error(f"No se pudo validar el basket. Error: {e}")
            raise

    def click_continue(self):
        """Usa un clic forzado con JavaScript para máxima robustez."""
        logger.info("Haciendo clic en Continuar para ir a la página de asientos (Seatmap).")
        wait = WebDriverWait(self.driver, 20)
        
        # 1. Esperamos solo a que el botón EXISTA en el DOM.
        continue_btn = wait.until(EC.presence_of_element_located(self.CONTINUE_BUTTON))
        
        # 2. Hacemos scroll hacia él.
        self.driver.execute_script("arguments[0].scrollIntoView(true);", continue_btn)
        time.sleep(1) # Pausa para que el scroll termine.
        
        # 3. FORZAMOS el clic con JavaScript.
        self.driver.execute_script("arguments[0].click();", continue_btn)
        
        logger.info("Clic forzado en 'Continuar' realizado.")
        
    def js_click_element(self, element):
        self.driver.execute_script("arguments[0].click();", element)
        time.sleep(3) # Aumentamos la pausa para ver la acción