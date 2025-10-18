# pages/seatmap_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.logger import get_logger
import time

logger = get_logger()

class SeatmapPage(BasePage):
    
    # --- LOCATORS ---
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    AVAILABLE_SEATS = (By.XPATH, "//button[contains(@class, 'seat') and not(contains(@class, 'unavailable')) and not(contains(@class, 'disabled'))]")
    CONTINUE_BUTTON = (By.XPATH, "//button[.//span[normalize-space()='Ir a pagar']]")

    def __init__(self, driver):
        super().__init__(driver)

    def select_seats_and_continue(self, num_passengers=1):
        """Método principal que selecciona asientos y continúa."""
        self.select_seats_for_all_passengers(num_passengers)
        self.click_continue()

    def select_seats_for_all_passengers(self, num_passengers=1):
        wait = WebDriverWait(self.driver, 45)
        
        logger.info("Esperando a que el mapa de asientos cargue...")
        try:
            wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
        except:
            pass
        
        wait.until(EC.element_to_be_clickable(self.AVAILABLE_SEATS))
        time.sleep(20)

        logger.info(f"Seleccionando asientos para {num_passengers} pasajero(s)...")
        
        for i in range(num_passengers):
            try:
        
                all_available_seats = self.driver.find_elements(*self.AVAILABLE_SEATS)
                logger.info(f"Iteración {i+1}: {len(all_available_seats)} asientos disponibles encontrados.")
                
                if not all_available_seats:
                    raise Exception("No se encontraron más asientos disponibles.")

                seat_to_select = all_available_seats[0]
                seat_number = seat_to_select.get_attribute("id") or seat_to_select.text
                
                logger.info(f"Seleccionando asiento '{seat_number}' para el pasajero {i+1}...")
                self.driver.execute_script("arguments[0].click();", seat_to_select)
                
                logger.info("Esperando a que la selección de asiento se procese...")
                time.sleep(15)

            except Exception as e:
                logger.error(f"No se pudo seleccionar el asiento para el pasajero {i+1}. Error: {e}")
                raise

    def click_continue(self):
        logger.info("Haciendo clic en 'Ir a pagar' para ir a la página de Pagos.")
        self.js_click(self.CONTINUE_BUTTON)