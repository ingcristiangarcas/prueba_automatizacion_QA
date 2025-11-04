# pages_roundtrip/select_flight_page_rt.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from pages_roundtrip.base_page import BasePage 
from utils.logger import get_logger 
import time
import allure

logger = get_logger()


def modal_calendar_day_locator(day: str, month: str, year: str):
    aria_label_date = f"{int(day)}-{int(month)}-{year}"
    return (By.XPATH, f"//div[contains(@class, 'ngb-dp-day') and @aria-label='{aria_label_date}']")


class SelectFlightPageRT(BasePage): 


    EDIT_SEARCH_TRIGGER = (By.XPATH, "//button[contains(@class, 'combined_summary_bar_button')][.//span[normalize-space()='Editar']]")
    MODAL_ORIGIN_BUTTON = (By.ID, "originBtn") 
    MODAL_ORIGIN_INPUT = (By.ID, "departureStationInputId") 
    MODAL_AUTOCOMPLETE_OPTION_MGA = (By.ID, "MGA") 
    MODAL_DESTINATION_BUTTON = (By.XPATH, "//input[@id='arrivalStationInputId']/ancestor::button[contains(@class, 'control_field_button')]")
    MODAL_DESTINATION_INPUT = (By.ID, "arrivalStationInputId")
    MODAL_AUTOCOMPLETE_OPTION_MDE = (By.ID, "MDE")
    MODAL_DEPARTURE_DATE_INPUT = (By.ID, "departureDateInputId") 
    MODAL_RETURN_DATE_INPUT = (By.ID, "returnDateInputId") 
    MODAL_ADULT_PLUS_BUTTON = (By.XPATH, "//div[contains(@class,'control_options_inner')]//li[.//div[contains(text(), 'Adultos')]]//button[contains(@class, 'plus')]") 
    MODAL_CONFIRM_PASSENGERS_BUTTON = (By.XPATH, "//div[contains(@class,'control_options_inner')]//button[.//span[normalize-space()='Confirmar']]")
    MODAL_APPLY_SEARCH_BUTTON = (By.ID, "searchButton") 
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    PRICE_BUTTON_DEPARTURE = (By.XPATH, "(//button[contains(@class, 'journey_price_button')])[1]")
    SELECT_FARE_BUTTON_DEPARTURE = (By.XPATH, "(//button[contains(@class, 'fare_button')][.//span[normalize-space()='Seleccionar']])[1]")
    PRICE_BUTTON_RETURN = (By.XPATH, "//h2[.//span[contains(text(), 'Vuelta')]]/following::button[contains(@class, 'journey_price_button')][1]")
    SELECT_FARE_BUTTON_RETURN = (By.XPATH, "(//button[contains(@class, 'fare_button')][.//span[normalize-space()='Seleccionar']])[1]")
    SUMMARY_TRIGGER = (By.CSS_SELECTOR, "button.summary_trigger")
    SUMMARY_PRICE_DETAIL_BUTTON = (By.CSS_SELECTOR, "button.price-breakdown-header")
    SUMMARY_CLOSE_BUTTON = (By.CSS_SELECTOR, "button.summary_close_btn")
    SUMMARY_BASKET_CONTENT = (By.ID, "summaryTypologyPerBookingId") 
    CONTINUE_BUTTON = (By.XPATH, "//button[contains(@class, 'page_button')]")

    def __init__(self, driver):
        super().__init__(driver)

    @allure.step("Hacer clic en el botón 'Editar' Búsqueda")
    def click_edit_booking_button(self):
        wait = WebDriverWait(self.driver, 60); 
        try: wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER)) 
        except TimeoutException: pass
        edit_button = wait.until(EC.element_to_be_clickable(self.EDIT_SEARCH_TRIGGER)); 
        try: self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", edit_button); time.sleep(0.5); edit_button.click()
        except ElementClickInterceptedException: logger.warning("Clic normal interceptado, intentando JS."); self.js_click(self.EDIT_SEARCH_TRIGGER)
        wait.until(EC.visibility_of_element_located(self.MODAL_ORIGIN_BUTTON)); logger.info("Modal OK.")

    @allure.step("Editar Origen a Managua (MGA) en el modal")
    def edit_origin_to_managua(self):
        wait = WebDriverWait(self.driver, 30); short_wait = WebDriverWait(self.driver, 10); origin_code = "MGA"; text_to_type = "Mana"
        try:
            wait.until(EC.element_to_be_clickable(self.MODAL_ORIGIN_BUTTON)).click()
            origin_input = wait.until(EC.visibility_of_element_located(self.MODAL_ORIGIN_INPUT)); origin_input.clear(); self.send_keys_slowly(self.MODAL_ORIGIN_INPUT, text_to_type) 
            mga_option = short_wait.until(EC.element_to_be_clickable(self.MODAL_AUTOCOMPLETE_OPTION_MGA)); mga_option.click(); time.sleep(1) 
        except Exception as e: logger.error(f"Error editando origen a {origin_code}: {e}"); self.take_screenshot(f"error_origen_{origin_code}.png"); raise

    @allure.step("Editar Destino a Medellín (MDE) en el modal")
    def edit_destination_to_medellin(self):
        wait = WebDriverWait(self.driver, 30); short_wait = WebDriverWait(self.driver, 10); dest_code = "MDE"; text_to_type = "Mede" 
        try:
            logger.info(f"Editando destino a: {dest_code}"); dest_input = wait.until(EC.visibility_of_element_located(self.MODAL_DESTINATION_INPUT))
            time.sleep(0.5); dest_input.click(); dest_input.clear()
            self.send_keys_slowly(self.MODAL_DESTINATION_INPUT, text_to_type); 
            mde_option = short_wait.until(EC.element_to_be_clickable(self.MODAL_AUTOCOMPLETE_OPTION_MDE)); self.js_click(self.MODAL_AUTOCOMPLETE_OPTION_MDE) 
            logger.info(f"Destino cambiado a {dest_code}."); time.sleep(1) 
        except Exception as e: logger.error(f"Error editando destino a {dest_code}: {e}"); self.take_screenshot(f"error_destino_{dest_code}.png"); raise

    @allure.step("Editar Fecha de Ida a {day}/{month}/{year} en el modal")
    def edit_departure_date(self, day: str, month: str, year: str):
        wait = WebDriverWait(self.driver, 30)
        try:
            logger.info(f"Editando fecha de ida a: {day}/{month}/{year}")
            logger.info("Esperando a que el calendario de ida sea visible (buscando día 1)...")
            day_1_locator = modal_calendar_day_locator("1", month, year)
            wait.until(EC.visibility_of_element_located(day_1_locator))
            dep_day_locator = modal_calendar_day_locator(day, month, year)
            logger.info(f"Esperando a que el día {day} sea clickeable...")
            dep_day_element = wait.until(EC.element_to_be_clickable(dep_day_locator))
            logger.info(f"Haciendo clic en el día {day}.")
            try:
                 self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", dep_day_element)
                 time.sleep(0.5); dep_day_element.click()
            except ElementClickInterceptedException:
                 logger.warning("Clic normal interceptado en día de ida, intentando JS."); self.js_click(dep_day_locator)
            logger.info(f"Fecha de ida cambiada a {day}/{month}/{year}."); time.sleep(1) 
        except Exception as e: logger.error(f"Falló al intentar cambiar la fecha de ida a {day}/{month}/{year}. Error: {e}"); self.take_screenshot(f"error_editando_fecha_ida.png"); raise

    # ---  MÉTODO PARA EDITAR FECHA DE REGRESO ---
    @allure.step("Editar Fecha de Ida a {day}/{month}/{year} en el modal")
    def edit_return_date(self, day: str, month: str, year: str):
        wait = WebDriverWait(self.driver, 30)
        try:
            logger.info(f"Editando fecha de regreso a: {day}/{month}/{year}")
            logger.info("Esperando a que el calendario de regreso sea visible (buscando día 1)...")
            day_1_locator = modal_calendar_day_locator("1", month, year)
            wait.until(EC.visibility_of_element_located(day_1_locator))
            ret_day_locator = modal_calendar_day_locator(day, month, year)
            logger.info(f"Esperando a que el día {day} sea clickeable...")
            ret_day_element = wait.until(EC.element_to_be_clickable(ret_day_locator))
            logger.info(f"Haciendo clic en el día {day}.")
            try:
                 self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", ret_day_element)
                 time.sleep(0.5); ret_day_element.click()
            except ElementClickInterceptedException:
                 logger.warning("Clic normal interceptado en día de regreso, intentando JS."); self.js_click(ret_day_locator)
            logger.info(f"Fecha de ida cambiada a {day}/{month}/{year}."); time.sleep(1.5) 
        except Exception as e: logger.error(f"Falló al intentar cambiar la fecha de regreso a {day}/{month}/{year}. Error: {e}"); self.take_screenshot(f"error_editando_fecha_regreso.png"); raise

    # --- MÉTODO PARA EDITAR PASAJEROS ---
    @allure.step("Editar Pasajeros al máximo ({max_pax}) en el modal")
    def edit_passengers_to_max(self, max_pax: int):
        wait = WebDriverWait(self.driver, 30)
        short_wait = WebDriverWait(self.driver, 10)
        
        try:
            logger.info("Selector de pasajeros abierto. Añadiendo adultos...")
            
            logger.info("Esperando a que el botón '+' de Adultos sea clickeable...")
            wait.until(EC.element_to_be_clickable(self.MODAL_ADULT_PLUS_BUTTON))

            logger.info(f"Añadiendo adultos hasta llegar a {max_pax}...")
            for i in range(max_pax - 1):
                try:
                    adult_plus_btn = short_wait.until(EC.element_to_be_clickable(self.MODAL_ADULT_PLUS_BUTTON))
                    adult_plus_btn.click() 
                except ElementClickInterceptedException:
                     logger.warning(f"Clic normal interceptado en '+' adulto {i+2}, intentando JS click.")
                     self.js_click(self.MODAL_ADULT_PLUS_BUTTON) 
                logger.debug(f"Clic {i+1} en '+' adulto.")
                time.sleep(0.5)

            logger.info("Esperando botón 'Confirmar Pasajeros'...")
            confirm_pax_btn = wait.until(EC.element_to_be_clickable(self.MODAL_CONFIRM_PASSENGERS_BUTTON))
            logger.info("Confirmando selección de pasajeros.")
            try:
                confirm_pax_btn.click() 
            except ElementClickInterceptedException:
                logger.warning("Clic normal interceptado en Confirmar Pax, intentando JS click.")
                self.js_click(self.MODAL_CONFIRM_PASSENGERS_BUTTON) 
            time.sleep(1)

        except Exception as e:
            logger.error(f"Falló al intentar cambiar el número de pasajeros a {max_pax}. Error: {e}")
            self.take_screenshot(f"error_editando_pasajeros.png")
            raise
    @allure.step("Aplicar cambios y Buscar Vuelos")
    def click_apply_search(self):
        wait = WebDriverWait(self.driver, 30)
        
        try:
            logger.info("Esperando botón 'Buscar'...")
            search_btn = wait.until(EC.element_to_be_clickable(self.MODAL_APPLY_SEARCH_BUTTON))
            logger.info("Haciendo clic en el botón 'Buscar'.")
            try:
                search_btn.click() 
            except ElementClickInterceptedException:
                 logger.warning("Clic normal interceptado en Buscar, intentando JS click.")
                 self.js_click(self.MODAL_APPLY_SEARCH_BUTTON) 
            
            logger.info("Esperando a que la página de 'Select Flight' se recargue...")
            WebDriverWait(self.driver, 90).until(EC.invisibility_of_element_located(self.PAGE_LOADER))
            logger.info("Loader desaparecido. Página 'Select Flight' recargada.")
        
        except Exception as e:
            logger.error(f"Falló al hacer clic en 'Buscar' o al esperar la recarga. Error: {e}")
            self.take_screenshot("error_aplicar_busqueda.png")
            raise
    
    # --- NUEVO MÉTODO PARA SELECCIONAR TARIFA DE IDA ---
    @allure.step("Seleccionar Tarifa de Vuelo de IDA")
    def select_departure_fare(self):
        wait = WebDriverWait(self.driver, 90)
        short_wait = WebDriverWait(self.driver, 20)
        
        try:
            logger.info("Esperando a que el loader (si existe) desaparezca...")
            try:
                wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
            except TimeoutException:
                logger.warning("Loader no apareció o tardó demasiado en desaparecer.")

            logger.info("Esperando botón de precio de IDA...")
            price_button_dep = wait.until(EC.element_to_be_clickable(self.PRICE_BUTTON_DEPARTURE))
            logger.info("Haciendo clic en precio de IDA.")
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", price_button_dep)
                time.sleep(0.5)
                price_button_dep.click()
            except ElementClickInterceptedException:
                logger.warning("Clic interceptado en precio IDA, reintentando JS.")
                self.js_click(self.PRICE_BUTTON_DEPARTURE)
            
            time.sleep(1.5)

            logger.info("Esperando botón 'Seleccionar' tarifa de IDA...")
            fare_button_dep = short_wait.until(EC.element_to_be_clickable(self.SELECT_FARE_BUTTON_DEPARTURE))
            logger.info("Haciendo clic en 'Seleccionar' tarifa IDA.")
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", fare_button_dep)
                time.sleep(0.5)
                fare_button_dep.click()
            except ElementClickInterceptedException:
                logger.warning("Clic interceptado en 'Seleccionar' IDA, reintentando JS.")
                self.js_click(self.SELECT_FARE_BUTTON_DEPARTURE)

            logger.info("Tarifa de IDA seleccionada.")
            logger.info("Esperando loader post-selección de tarifa IDA...")
            wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
            logger.info("Loader desaparecido.")
            
        except Exception as e:
            logger.error(f"Falló durante la selección de tarifa de IDA. Error: {e}")
            self.take_screenshot("error_seleccion_tarifa_ida.png")
            raise

    # --- MÉTODO DE REGRESO ---
    @allure.step("Seleccionar Tarifa de Vuelo de REGRESO")
    def select_return_fare(self):
        wait = WebDriverWait(self.driver, 90)
        short_wait = WebDriverWait(self.driver, 20)
        
        try:
            logger.info("Esperando botón de precio de REGRESO (basado en h2 'Vuelta')...")
            price_button_ret = wait.until(EC.element_to_be_clickable(self.PRICE_BUTTON_RETURN))
            logger.info("Haciendo clic en precio de REGRESO.")
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", price_button_ret)
                time.sleep(0.5)
                price_button_ret.click()
            except ElementClickInterceptedException:
                logger.warning("Clic interceptado en precio REGRESO, reintentando JS.")
                self.js_click(self.PRICE_BUTTON_RETURN)
            
            time.sleep(1.5)

            logger.info("Esperando botón 'Seleccionar' tarifa de REGRESO...")
            fare_button_ret = short_wait.until(EC.element_to_be_clickable(self.SELECT_FARE_BUTTON_RETURN))
            logger.info("Haciendo clic en 'Seleccionar' tarifa REGRESO.")
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", fare_button_ret)
                time.sleep(0.5)
                fare_button_ret.click()
            except ElementClickInterceptedException:
                logger.warning("Clic interceptado en 'Seleccionar' REGRESO, reintentando JS.")
                self.js_click(self.SELECT_FARE_BUTTON_RETURN)

            logger.info("Tarifa de REGRESO seleccionada.")
            logger.info("Esperando loader post-selección de tarifa REGRESO...")
            wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
            logger.info("Loader desaparecido.")
            
        except Exception as e:
            logger.error(f"Falló durante la selección de tarifa de REGRESO. Error: {e}")
            self.take_screenshot("error_seleccion_tarifa_regreso.png")
            raise

    # --- MÉTODO DE VALIDACIÓN DE SUMMARY ---
    @allure.step("Validar Revisión en Summary (con 'Ver detalle')")
    def validate_summary(self):
        wait = WebDriverWait(self.driver, 30)
        logger.info("Abriendo el resumen de compra (Summary) para validación.")
        try:
            # 1. Abrir el Summary
            logger.info("Esperando que el gatillo del summary sea clickeable...")
            wait.until(EC.element_to_be_clickable(self.SUMMARY_TRIGGER))
            self.js_click(self.SUMMARY_TRIGGER) 
            time.sleep(1.0)

            # 2. Clic en "Ver detalle"
            logger.info("Haciendo clic en 'Ver detalle'...")
            wait.until(EC.element_to_be_clickable(self.SUMMARY_PRICE_DETAIL_BUTTON))
            self.js_click(self.SUMMARY_PRICE_DETAIL_BUTTON)
            time.sleep(1.5)

            # 3. Validar (Aserción)
            logger.info("Esperando que el contenido del basket sea visible...")
            basket_element = wait.until(EC.visibility_of_element_located(self.SUMMARY_BASKET_CONTENT))
            basket_text = basket_element.text
            logger.info("Validación visual del summary (clics exitosos).")
            allure.attach(f"Texto del Summary: {basket_text}", name="Validación del Summary", attachment_type=allure.attachment_type.TEXT)

            
            # 4. Cerrar el Summary
            logger.info("Cerrando el resumen de compra.")
            close_button = wait.until(EC.element_to_be_clickable(self.SUMMARY_CLOSE_BUTTON))
            self.js_click(self.SUMMARY_CLOSE_BUTTON)
            time.sleep(1.5)
        
        except AssertionError as e:
            logger.error(f"FALLO DE ASERCIÓN en Summary: {e}")
            self.take_screenshot("error_screenshot_summary_validation.png")
            raise
        except Exception as e:
            logger.error(f"Error durante la validación del Summary: {e}")
            self.take_screenshot("error_screenshot_summary_error.png")
            raise

    @allure.step("Hacer clic en 'Continuar' a Pasajeros")
    def click_continue_to_passengers(self):
        wait = WebDriverWait(self.driver, 30)
        try:
            logger.info("Haciendo clic en 'Continuar' para ir a la página de pasajeros.")
            continue_button = wait.until(EC.element_to_be_clickable(self.CONTINUE_BUTTON))
            try:
                 continue_button.click()
            except ElementClickInterceptedException:
                 logger.warning("Clic normal interceptado en Continuar, intentando JS.")
                 self.js_click(self.CONTINUE_BUTTON)
        except Exception as e:
            logger.error(f"Falló al hacer clic en 'Continuar' a Pasajeros. Error: {e}")
            self.take_screenshot("error_clic_continuar_pax.png")
            raise