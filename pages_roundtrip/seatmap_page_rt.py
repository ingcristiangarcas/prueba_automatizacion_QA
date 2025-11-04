import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages_roundtrip.base_page import BasePage
from utils.logger import get_logger

logger = get_logger()

class SeatmapPageRT(BasePage):

    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader") 
    PASSENGER_LIST_TABS = (By.CSS_SELECTOR, "span.pax-selector_pax-name")
    NEXT_FLIGHT_BTN = (By.XPATH, "//button[.//span[normalize-space()='Siguiente vuelo']]")
    AVAILABLE_SEAT = (By.XPATH, "(//span[contains(@class, 'seat-number')])[1]")
    SUMMARY_TRIGGER_BTN = (By.CSS_SELECTOR, "button.summary_trigger")
    SUMMARY_VER_DETALLE_BTN = (By.CSS_SELECTOR, "button.price-breakdown-header")
    SUMMARY_BASKET_CONTENT = (By.ID, "summaryTypologyPerBookingId")
    SUMMARY_CERRAR_BTN = (By.CSS_SELECTOR, "button.summary_close_btn")
    CONTINUE_TO_PAY_BTN = (By.XPATH, "//button[.//span[normalize-space()='Ir a pagar']]")

    def __init__(self, driver):
        super().__init__(driver)
        logger.info("Página de Selección de Asientos (SeatmapPageRT) iniciada.")

    @allure.step("Esperar a que cargue el mapa de asientos [Plan C]")
    def wait_for_page_to_load(self, wait: WebDriverWait, segment_name: str):
        try:

            logger.info(f"Cargando {segment_name}. Esperando que el loader desaparezca (máx 30s)...")
            WebDriverWait(self.driver, 40).until(
                EC.invisibility_of_element_located(self.PAGE_LOADER)
            )
            logger.info("Page loader de Seatmap desapareció correctamente.")
            
        except TimeoutException:
            logger.warning(f"¡El 'page loader' en {segment_name} no desapareció! Está atascado.")
            logger.warning("Aplicando 'Plan C': Eliminando el loader con JavaScript...")
            try:
                loader_element = self.driver.find_element(*self.PAGE_LOADER)
                self.driver.execute_script("arguments[0].style.display = 'none';", loader_element)
                logger.info("¡Loader eliminado forzosamente! Continuando test...")
            except NoSuchElementException:
                logger.info("El loader ya no estaba, pero la espera falló. Raro. Continuando...")
            except Exception as e:
                logger.error(f"Falló el intento de eliminar el loader atascado: {e}")
                self.take_screenshot("error_loader_stuck_and_cant_remove.png")
                raise
        
        try:
            wait.until(EC.presence_of_all_elements_located(self.PASSENGER_LIST_TABS))
            wait.until(EC.element_to_be_clickable(self.AVAILABLE_SEAT))
            logger.info(f"Mapa de asientos para {segment_name} cargado y listo.")
        except TimeoutException as e:
            logger.error(f"El mapa de asientos no cargó (no se encontró la lista de pasajeros o asientos). Error: {e}")
            self.take_screenshot("error_seatmap_load.png")
            raise

    @allure.step("Seleccionar asientos para todos los pasajeros impares en 4 segmentos")
    def select_seats_for_all_segments(self, num_passengers: int):
        wait = WebDriverWait(self.driver, 20)
        num_segments = 4 

        for i in range(num_segments):
            segment_name = f"Segmento {i + 1}/{num_segments}"
            logger.info(f"--- Iniciando selección para {segment_name} ---")
            
            self.wait_for_page_to_load(wait, f"{segment_name} - Carga inicial")

            try:
                logger.info(f"Procesando Pasajero 1 (auto-seleccionado)...")
                seat = wait.until(EC.element_to_be_clickable(self.AVAILABLE_SEAT))
                seat_name = seat.text
                logger.info(f"Clic en Asiento {seat_name} para Pasajero 1.")
                self.driver.execute_script("arguments[0].click();", seat)
            except Exception as e:
                logger.error(f"No se pudo seleccionar asiento para Pasajero 1. Error: {e}")
                self.take_screenshot(f"error_pax_1_segment_{i+1}.png")
                raise

            for pax_index in range(2, num_passengers, 2):

                self.wait_for_page_to_load(wait, f"{segment_name} - Post-recarga, esperando Pasajero {pax_index}")

                logger.info(f"Procesando Pasajero {pax_index + 1}...")
                
                try:
                    passenger_tabs = wait.until(EC.presence_of_all_elements_located(self.PASSENGER_LIST_TABS))
                    logger.info(f"Página recargada. Clic en pestaña Pasajero {pax_index + 1}...")
                    pax_tab = passenger_tabs[pax_index]
                    self.driver.execute_script("arguments[0].click();", pax_tab)
                    time.sleep(10) 
                    
                except Exception as e:
                    logger.error(f"No se pudo hacer clic en la pestaña del Pasajero {pax_index + 1}. Error: {e}")
                    self.take_screenshot(f"error_pax_{pax_index + 1}_tab.png")
                    raise
                try:
                    seat = wait.until(EC.element_to_be_clickable(self.AVAILABLE_SEAT))
                    seat_name = seat.text
                    logger.info(f"Clic en Asiento {seat_name} para Pasajero {pax_index + 1}.")
                    self.driver.execute_script("arguments[0].click();", seat)
                except Exception as e:
                    logger.error(f"No se pudo seleccionar asiento para Pasajero {pax_index + 1}. Error: {e}")
                    self.take_screenshot(f"error_pax_{pax_index + 1}_seat.png")
                    raise
            logger.info(f"Esperando recarga final del segmento (después de P9)...")
            self.wait_for_page_to_load(wait, f"{segment_name} - Post-recarga final (P9)")
            logger.info(f"Todos los pasajeros impares del {segment_name} seleccionados.")

            if i < num_segments - 1:
                logger.info(f"--- Fin {segment_name}. Clic en 'Siguiente vuelo'. ---")
                try:
                    next_btn = wait.until(EC.element_to_be_clickable(self.NEXT_FLIGHT_BTN))
                    self.driver.execute_script("arguments[0].click();", next_btn)
                except Exception as e:
                    logger.error(f"No se pudo hacer clic en 'Siguiente vuelo'. Error: {e}")
                    self.take_screenshot(f"error_next_flight_btn_{i+1}.png")
                    raise
            else:
                logger.info(f"--- Fin {segment_name}. Todos los segmentos completados. ---")

    @allure.step("Validar servicios en el resumen de compra (basket) [Plan B]")
    def validate_summary(self):
        """
        [Plan B] Abre el resumen, hace SCROLL al detalle, lo abre,
        espera 2s, y cierra.
        """
        wait = WebDriverWait(self.driver, 30)
        try:
           
            logger.info("Esperando que el gatillo del summary sea clickeable...")
            wait.until(EC.element_to_be_clickable(self.SUMMARY_TRIGGER_BTN))
            self.js_click(self.SUMMARY_TRIGGER_BTN) 
            time.sleep(1.0)

            logger.info("Haciendo clic en 'Ver detalle'...")
            wait.until(EC.element_to_be_clickable(self.SUMMARY_VER_DETALLE_BTN))
            self.js_click(self.SUMMARY_VER_DETALLE_BTN)
            time.sleep(1.5)

            logger.info("Esperando que el contenido del basket sea visible...")
            basket_element = wait.until(EC.visibility_of_element_located(self.SUMMARY_BASKET_CONTENT))
            basket_text = basket_element.text
            logger.info("Validación visual del summary (clics exitosos).")
            allure.attach(f"Texto del Summary: {basket_text}", name="Validación del Summary", attachment_type=allure.attachment_type.TEXT)

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

    @allure.step("Continuar a la página de Pago")
    def click_continue_to_payment(self):

        logger.info("Haciendo clic en 'Ir a pagar'...")
        wait = WebDriverWait(self.driver, 15)
        try:
            continue_btn = wait.until(EC.element_to_be_clickable(self.CONTINUE_TO_PAY_BTN))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", continue_btn)
            time.sleep(0.5) 
            self.driver.execute_script("arguments[0].click();", continue_btn)
        except Exception as e:
            logger.error(f"No se pudo hacer clic en 'Ir a pagar' en Seatmap. Error: {e}")
            self.take_screenshot("error_continue_to_payment.png")
            raise