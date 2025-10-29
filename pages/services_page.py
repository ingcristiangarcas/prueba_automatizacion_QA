# pages/services_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.logger import get_logger
import time
import allure

logger = get_logger()

class ServicesPage(BasePage):
    
    # --- LOCATORS ---
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    SERVICE_CARDS = (By.XPATH, "//card-component")
    # Título de la tarjeta de servicio (relativo a la tarjeta)
    CARD_TITLE = (By.XPATH, ".//div[contains(@class, 'services-card_title')]")
    # Botón "Añadir" en la tarjeta (relativo a la tarjeta)
    CARD_ADD_BUTTON = (By.XPATH, ".//button[contains(@class, 'services-card_action_button')]")
    
    # --- Locators DENTRO de los modales ---
    # (Estos son genéricos y funcionan para la mayoría de los modales)
    MODAL_ADD_PLUS_BUTTONS = (By.XPATH, "//div[contains(@class, 'modal-service_selector')]//button[contains(@class, 'ui-num-ud_button plus')]")
    MODAL_ADD_LABEL_BUTTON = (By.XPATH, "//div[contains(@class, 'modal-service_selector')]//label[contains(@class, 'service_item_button')]")
    MODAL_TERMS_CHECKBOX = (By.ID, "termsconditions")
    MODAL_CONFIRM_BUTTON = (By.XPATH, "//div[contains(@class, 'modal-service_selector')]//button[.//span[normalize-space()='Confirmar']]")
    MODAL_CONTINUE_BUTTON = (By.XPATH, "//div[contains(@class, 'modal-service_selector')]//button[.//span[normalize-space()='Continuar']]")
    
    # --- Locators del Basket/Summary ---
    BASKET_SUMMARY_TRIGGER = (By.CSS_SELECTOR, ".summary_trigger")
    BASKET_DETAIL_BUTTON = (By.CSS_SELECTOR, "button.price-breakdown-header")
    BASKET_CLOSE_BUTTON = (By.CSS_SELECTOR, "button.summary_close_btn")
    BASKET_CONTENT = (By.ID, "booking-summary-basket") # ID del contenido del basket

    CONTINUE_BUTTON = (By.CSS_SELECTOR, "div.page-actions button.btn-action")

    def __init__(self, driver):
        super().__init__(self)

    # --- ORQUESTADOR PARA CASO 1 ---
    @allure.step("Caso 1: Añadir TODOS los servicios disponibles y validar")
    def add_all_services_and_validate_basket_caso1(self):
        """Orquestador principal para el Caso 1."""
        self.add_all_available_services()
        # Validamos que se hayan añadido servicios (genérico)
        self.validate_basket_services(expected_services=["Equipaje", "Asiento"]) 
        self.click_continue()

    # --- ORQUESTADOR PARA CASO 2 ---
    @allure.step("Caso 2: Añadir equipaje (Carry-on, Checked, Sports) y validar")
    def add_specific_baggage_and_validate_basket_caso2(self, num_passengers):
        """Orquestador principal para el Caso 2."""
        self.add_specific_baggage(num_passengers)
        # Validamos los servicios específicos del Caso 2 
        self.validate_basket_services(expected_services=[
            "Equipaje de mano", 
            "Equipaje en bodega", 
            "Equipaje deportivo"
        ])
        self.click_continue()

    # --- LÓGICA CASO 1 ---
    def add_all_available_services(self):
        """
        Añade TODOS los servicios (Lógica para Caso 1).
        (Este es tu método original, sin cambios)
        """
        wait = WebDriverWait(self.driver, 25)
        logger.info("Esperando a que la página de servicios cargue...")
        try: wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
        except: pass
        wait.until(EC.presence_of_all_elements_located(self.SERVICE_CARDS))
        
        num_service_cards = len(self.driver.find_elements(*self.SERVICE_CARDS))
        logger.info(f"[Caso 1] Se encontraron {num_service_cards} tarjetas de servicio.")
        
        for i in range(num_service_cards):
            all_cards = wait.until(EC.presence_of_all_elements_located(self.SERVICE_CARDS))
            current_card = all_cards[i]
            title_text = current_card.find_element(*self.CARD_TITLE).text
            
            if "Asistencia especial" in title_text:
                logger.info(f"[Caso 1] Omitiendo servicio '{title_text}'.")
                continue

            logger.info(f"[Caso 1] Procesando servicio: '{title_text}'...")
            
            try:
                add_button = current_card.find_element(*self.CARD_ADD_BUTTON)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
                time.sleep(2.5)
                self.driver.execute_script("arguments[0].click();", add_button)
                time.sleep(3)

                # --- Lógica de Modal (Genérica) ---
                plus_buttons = self.driver.find_elements(*self.MODAL_ADD_PLUS_BUTTONS)
                if plus_buttons:
                    logger.info(f"Encontrados {len(plus_buttons)} botones '+' para '{title_text}'.")
                    for btn in plus_buttons: self.js_click_element(btn)
                
                label_buttons = self.driver.find_elements(*self.MODAL_ADD_LABEL_BUTTON)
                if label_buttons:
                    logger.info(f"Encontrado botón 'Añadir' (label) para '{title_text}'.")
                    self.js_click_element(label_buttons[0])
                
                terms_checkbox = self.driver.find_elements(*self.MODAL_TERMS_CHECKBOX)
                if terms_checkbox:
                    logger.info(f"Encontrado checkbox de términos para '{title_text}'.")
                    self.js_click_element(terms_checkbox[0])

                confirm_buttons = self.driver.find_elements(*self.MODAL_CONFIRM_BUTTON)
                if confirm_buttons:
                    logger.info(f"Confirmando servicio '{title_text}'.")
                    self.js_click_element(confirm_buttons[0])
                
                time.sleep(4) 
            except Exception as e:
                logger.error(f"[Caso 1] Error procesando el servicio '{title_text}': {e}")
                self.take_screenshot(f"error_servicio_{title_text}.png")
                # Cerramos el modal si falló para no bloquear el script
                self.driver.get(self.driver.current_url) 
                time.sleep(2)
    
    # --- LÓGICA CASO 2 (NUEVO) ---
    def add_specific_baggage(self, num_passengers):
        """
        Añade solo equipaje normal (Carry/Checked) y deportivo.
        Lógica para Caso 2. [cite: 70]
        """
        # Nombres de los servicios requeridos
        services_to_add = ["Equipaje de mano", "Equipaje en bodega", "Equipaje deportivo"]
        
        wait = WebDriverWait(self.driver, 25)
        logger.info("Esperando a que la página de servicios cargue...")
        try: wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
        except: pass
        wait.until(EC.presence_of_all_elements_located(self.SERVICE_CARDS))
        
        all_cards = self.driver.find_elements(*self.SERVICE_CARDS)
        logger.info(f"[Caso 2] Se encontraron {len(all_cards)} tarjetas. Buscando equipaje...")

        for card in all_cards:
            title_text = card.find_element(*self.CARD_TITLE).text
            
            # Verificamos si el título de la tarjeta es uno de los que buscamos
            if any(service in title_text for service in services_to_add):
                logger.info(f"[Caso 2] Procesando servicio requerido: '{title_text}'...")
                
                try:
                    add_button = card.find_element(*self.CARD_ADD_BUTTON)
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
                    time.sleep(2.5)
                    self.driver.execute_script("arguments[0].click();", add_button)
                    time.sleep(3)

                    # --- Lógica de Modal (Específica para equipaje) ---
                    # Requisito: "para todos los pasajeros" [cite: 70]
                    # Tu localizador 'MODAL_ADD_PLUS_BUTTONS' encuentra todos los botones '+'
                    # Esta lógica hará clic en todos ellos (uno por pasajero)
                    plus_buttons = wait.until(EC.presence_of_all_elements_located(self.MODAL_ADD_PLUS_BUTTONS))
                    
                    if len(plus_buttons) < num_passengers:
                        logger.warning(f"Se esperaban {num_passengers} botones '+' pero se encontraron {len(plus_buttons)}")
                    
                    logger.info(f"Añadiendo '{title_text}' para {len(plus_buttons)} pasajeros...")
                    for btn in plus_buttons:
                        self.js_click_element(btn)
                        time.sleep(0.5) # Pausa entre clics

                    # (Tu lógica genérica para 'label_buttons' y 'terms_checkbox' es buena si aplica)
                    
                    confirm_buttons = self.driver.find_elements(*self.MODAL_CONFIRM_BUTTON)
                    if confirm_buttons:
                        logger.info(f"Confirmando servicio '{title_text}'.")
                        self.js_click_element(confirm_buttons[0])
                    
                    time.sleep(4)
                
                except Exception as e:
                    logger.error(f"[Caso 2] Error procesando el servicio '{title_text}': {e}")
                    self.take_screenshot(f"error_servicio_{title_text}.png")
                    self.driver.get(self.driver.current_url) 
                    time.sleep(2)
            else:
                logger.debug(f"[Caso 2] Omitiendo servicio '{title_text}'.")

    # --- MÉTODO COMPARTIDO (MEJORADO) ---
    def validate_basket_services(self, expected_services: list):
        """
        Abre, expande detalles y VALIDA (ASERCIÓN) que los servicios
        esperados estén en el basket. 
        """
        wait = WebDriverWait(self.driver, 20)
        logger.info("Validando el basket de compra...")
        
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1) # Pausa post-scroll

            logger.info("Abriendo el resumen de compra (Summary).")
            summary_trigger = wait.until(EC.element_to_be_clickable(self.BASKET_SUMMARY_TRIGGER))
            self.driver.execute_script("arguments[0].click();", summary_trigger)
            
            # Esperar a que el basket esté visible
            basket_element = wait.until(EC.visibility_of_element_located(self.BASKET_CONTENT))
            
            # --- ASERCIÓN ---
            logger.info("Realizando aserción del contenido del basket...")
            basket_text = basket_element.text
            
            for service in expected_services:
                assert service in basket_text, f"FALLO DE ASERCIÓN: El servicio '{service}' NO se encontró en el basket."
                logger.info(f"ASERCIÓN EXITOSA: Servicio '{service}' validado en el basket.")
            
            allure.attach(basket_text, name="Contenido del Basket Validado", attachment_type=allure.attachment_type.TEXT)
            time.sleep(1)
            
            logger.info("Cerrando el resumen de compra.")
            close_button = wait.until(EC.element_to_be_clickable(self.BASKET_CLOSE_BUTTON))
            self.driver.execute_script("arguments[0].click();", close_button)
            time.sleep(1)
            logger.info("Basket validado con éxito.")

        except AssertionError as e:
            logger.error(f"FALLO DE ASERCIÓN: {e}")
            self.take_screenshot("error_validacion_basket.png")
            raise
        except Exception as e:
            logger.error(f"No se pudo validar el basket. Error: {e}")
            self.take_screenshot("error_abriendo_basket.png")
            raise

    def click_continue(self):
        """Usa un clic forzado con JavaScript para máxima robustez."""
        logger.info("Haciendo clic en Continuar para ir a la página de asientos (Seatmap).")
        wait = WebDriverWait(self.driver, 20)
        
        continue_btn = wait.until(EC.presence_of_element_located(self.CONTINUE_BUTTON))
        
        self.driver.execute_script("arguments[0].scrollIntoView(true);", continue_btn)
        time.sleep(1) 
        
        self.driver.execute_script("arguments[0].click();", continue_btn)
        
        logger.info("Clic forzado en 'Continuar' realizado.")
        
    def js_click_element(self, element):
        """Clic con JS y una pausa fija (como la tenías)."""
        self.driver.execute_script("arguments[0].click();", element)
        time.sleep(3) # Tu pausa original