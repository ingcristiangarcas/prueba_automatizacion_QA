# pages/offers_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from pages.base_page import BasePage
from utils.logger import get_logger
import allure
import time

logger = get_logger()

# (Las funciones de localizador de calendario no se usan por ahora)
# def calendar_day_css_locator(...):
# def return_calendar_day_css_locator(...):

class OffersPage(BasePage):

    # --- LOCATORS ---
    OFFER_IMAGE = (By.CSS_SELECTOR, ".routes-lowest-price-list_grid--cols-3 > .routes-lowest-price-list_item:nth-child(2) .route-lowest-price_image")
    SEARCH_BUTTON = (By.ID, "searchButton") # Botón "Buscar" principal
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")

    def __init__(self, driver):
        super().__init__(driver)

    @allure.step("Seleccionar oferta y Buscar con valores por defecto")
    def select_offer_and_search_defaults(self):
        """
        Hace clic en la oferta y luego directamente en Buscar, 
        usando fechas/pasajeros por defecto.
        """
        wait = WebDriverWait(self.driver, 45) 

        try:
            # --- 1. Clic en la Oferta (Imagen) ---
            logger.info("Esperando a que la imagen de la oferta sea clickeable...")
            wait.until(EC.element_to_be_clickable(self.OFFER_IMAGE))
            logger.info("Haciendo clic en la imagen de la oferta.")
            self.js_click(self.OFFER_IMAGE) 
            time.sleep(1.0) # Pausa para que aparezcan opciones

            # --- 2. Iniciar Búsqueda (Sin tocar fechas/pasajeros) ---
            logger.info("Esperando botón 'Buscar'...")
            search_btn = wait.until(EC.element_to_be_clickable(self.SEARCH_BUTTON))
            logger.info("Haciendo clic en el botón 'Buscar'.")
            try:
                search_btn.click() 
            except ElementClickInterceptedException:
                 logger.warning("Clic normal interceptado en Buscar, intentando JS click.")
                 self.js_click(self.SEARCH_BUTTON) 
            logger.info("Esperando a que la página de 'Select Flight' cargue...")
            try:
                WebDriverWait(self.driver, 60).until(EC.invisibility_of_element_located(self.PAGE_LOADER))
                logger.info("Loader desaparecido. Página 'Select Flight' cargada.")
            except TimeoutException:
                 logger.warning("El loader post-búsqueda no apareció o tardó demasiado.")

        except Exception as e:
            logger.error(f"Falló durante la selección de oferta y búsqueda simple: {e}")
            self.take_screenshot("error_oferta_simple.png")
            raise