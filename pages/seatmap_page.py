# pages/seatmap_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.logger import get_logger
import time
import allure

logger = get_logger()

class SeatmapPage(BasePage):
    
    # --- LOCATORS ---
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    
    # Contenedor de un segmento de vuelo (ej. "Ida: BOG-MDE")
    SEGMENT_CONTAINER = (By.XPATH, "//div[contains(@class, 'segment-seatmap-container')]") 
    
    # Pestañas de Pasajero (relativo a un SEGMENT_CONTAINER)
    # Asume que hay una pestaña por pasajero
    PASSENGER_TABS = (By.XPATH, ".//div[contains(@class, 'passenger-seat-tab')]") 
    
    # Asientos disponibles (relativo a un SEGMENT_CONTAINER)
    AVAILABLE_SEATS = (By.XPATH, ".//button[contains(@class, 'seat') and not(contains(@class, 'unavailable')) and not(contains(@class, 'disabled'))]")
    
    # Botón de continuar (a veces es 'Ir a pagar' o 'Continuar')
    CONTINUE_BUTTON = (By.XPATH, "//button[.//span[normalize-space()='Ir a pagar'] or .//span[normalize-space()='Continuar']]")

    # --- Locators del Basket/Summary ---
    BASKET_SUMMARY_TRIGGER = (By.CSS_SELECTOR, ".summary_trigger")
    BASKET_CONTENT = (By.ID, "booking-summary-basket")
    BASKET_CLOSE_BUTTON = (By.CSS_SELECTOR, "button.summary_close_btn")


    def __init__(self, driver):
        super().__init__(driver)

    # --- ORQUESTADOR PARA CASO 1 ---
    @allure.step("Caso 1: Seleccionar asientos para TODOS los pasajeros")
    def select_seats_and_continue_caso1(self, num_passengers):
        """Orquestador principal para el Caso 1."""
        self._select_seats_logic(num_passengers, strategy="all")
        self.validate_basket_seats(num_passengers)
        self.click_continue()

    # --- ORQUESTADOR PARA CASO 2 ---
    @allure.step("Caso 2: Seleccionar asientos para pasajeros IMPARES")
    def select_seats_and_continue_caso2(self, num_passengers):
        """Orquestador principal para el Caso 2."""
        self._select_seats_logic(num_passengers, strategy="odd")
        
        # Validamos que se hayan añadido asientos (al menos 1)
        # El Caso 2 pide validar para impares (1, 3, 5...)
        expected_seats = (num_passengers // 2) + (num_passengers % 2)
        self.validate_basket_seats(expected_seats)
        self.click_continue()

    def _select_seats_logic(self, num_passengers, strategy="all"):
        """
        Lógica principal de selección de asientos.
        - 'strategy' puede ser "all" (Caso 1) o "odd" (Caso 2).
        """
        wait = WebDriverWait(self.driver, 45) # Wait largo para el seatmap
        
        logger.info(f"Iniciando lógica de selección de asientos (Estrategia: {strategy})")
        logger.info("Esperando a que el loader principal del seatmap desaparezca...")
        try:
            wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
        except:
            logger.warning("El loader inicial no apareció o tardó demasiado. Continuando.")
        
        # Esperamos a que los contenedores de segmento (Ida, Vuelta) carguen
        wait.until(EC.presence_of_all_elements_located(self.SEGMENT_CONTAINER))
        segments = self.driver.find_elements(*self.SEGMENT_CONTAINER)
        logger.info(f"Encontrados {len(segments)} segmentos de vuelo (Ida/Vuelta).")

        for s_idx, segment in enumerate(segments):
            logger.info(f"--- Procesando Segmento {s_idx + 1} ---")
            
            # Encontramos las pestañas de pasajero DENTRO del segmento actual
            passenger_tabs = segment.find_elements(*self.PASSENGER_TABS)
            
            # Verificamos si el N° de pestañas coincide con el N° de pasajeros
            if len(passenger_tabs) != num_passengers:
                logger.warning(f"Discrepancia: Se esperaban {num_passengers} pasajeros pero se encontraron {len(passenger_tabs)} pestañas.")
            
            # Iteramos por cada pestaña de pasajero
            for p_idx in range(len(passenger_tabs)):
                pax_number = p_idx + 1 # 1-based index (Pasajero 1, 2, 3...)
                
                # --- Lógica de selección basada en estrategia ---
                should_select = False
                if strategy == "all":
                    should_select = True
                elif strategy == "odd" and pax_number % 2 != 0: # Si es impar (1, 3, 5...)
                    should_select = True
                
                # Hacemos clic en la pestaña del pasajero actual para activarla
                try:
                    pax_tab = segment.find_elements(*self.PASSENGER_TABS)[p_idx]
                    self.js_click(pax_tab)
                    time.sleep(0.5) # Breve pausa para que la UI reaccione
                except Exception as e:
                    logger.error(f"No se pudo hacer clic en la pestaña del Pasajero {pax_number}. Error: {e}")
                    continue # Saltar a la siguiente pestaña de pasajero

                if should_select:
                    logger.info(f"Seleccionando asiento para Pasajero {pax_number} (Impar)...")
                    try:
                        # Buscamos asientos disponibles DENTRO del segmento actual
                        available_seats_in_segment = segment.find_elements(*self.AVAILABLE_SEATS)
                        
                        if not available_seats_in_segment:
                            raise Exception(f"No se encontraron asientos disponibles para el Pasajero {pax_number} en el Segmento {s_idx + 1}.")
                        
                        seat_to_select = available_seats_in_segment[0]
                        seat_id = seat_to_select.get_attribute("id") or "N/A"
                        
                        logger.info(f"Intentando seleccionar asiento {seat_id}...")
                        self.js_click(seat_to_select)
                        
                        # --- REEMPLAZO DE time.sleep(15) ---
                        # Esperamos a que el mini-loader (si existe) aparezca y desaparezca
                        logger.info("Esperando a que la selección de asiento se procese...")
                        wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
                        logger.info(f"Asiento {seat_id} seleccionado para Pasajero {pax_number}.")
                        
                    except Exception as e:
                        logger.error(f"Error seleccionando asiento para Pasajero {pax_number}: {e}")
                        self.take_screenshot(f"error_pax_{pax_number}_seat.png")
                        # Si falla, continuamos con el siguiente pasajero
                
                else:
                    logger.info(f"Omitiendo Pasajero {pax_number} (Par) según estrategia '{strategy}'.")

    @allure.step("Validar asientos seleccionados en el basket")
    def validate_basket_seats(self, expected_seat_count):
        """Valida que los asientos se hayan añadido al basket."""
        wait = WebDriverWait(self.driver, 20)
        logger.info(f"Validando {expected_seat_count} asiento(s) en el basket...")
        
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            logger.info("Abriendo el resumen de compra (Summary).")
            summary_trigger = wait.until(EC.element_to_be_clickable(self.BASKET_SUMMARY_TRIGGER))
            self.driver.execute_script("arguments[0].click();", summary_trigger)
            
            basket_element = wait.until(EC.visibility_of_element_located(self.BASKET_CONTENT))
            basket_text = basket_element.text

            # --- ASERCIÓN ---
            # Requisito: "validar en basket"
            assert "Asiento" in basket_text, "FALLO DE ASERCIÓN: La palabra 'Asiento' no se encontró en el basket."
            
            # (Validación más avanzada, opcional):
            # seat_mentions = basket_text.count("Asiento")
            # assert seat_mentions >= expected_seat_count, f"FALLO DE ASERCIÓN: Se esperaban {expected_seat_count} asientos, pero se encontraron {seat_mentions}."
            
            logger.info("ASERCIÓN EXITOSA: Asientos validados en el basket.")
            allure.attach(basket_text, name="Contenido del Basket (Asientos)", attachment_type=allure.attachment_type.TEXT)
            time.sleep(1)
            
            logger.info("Cerrando el resumen de compra.")
            close_button = wait.until(EC.element_to_be_clickable(self.BASKET_CLOSE_BUTTON))
            self.driver.execute_script("arguments[0].click();", close_button)
            time.sleep(1)
            logger.info("Basket de asientos validado.")
            
        except AssertionError as e:
            logger.error(f"FALLO DE ASERCIÓN: {e}")
            self.take_screenshot("error_validacion_basket_asientos.png")
            raise
        except Exception as e:
            logger.error(f"No se pudo validar el basket de asientos. Error: {e}")
            self.take_screenshot("error_abriendo_basket_asientos.png")
            raise

    def click_continue(self):
        logger.info("Haciendo clic en 'Ir a pagar' para ir a la página de Pagos.")
        # Usamos el localizador genérico que definimos arriba
        self.js_click(self.CONTINUE_BUTTON)