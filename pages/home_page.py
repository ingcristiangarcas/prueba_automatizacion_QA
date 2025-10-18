# pages/home_page.py
import time
from pages.base_page import BasePage
from utils.logger import get_logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

logger = get_logger()

class HomePage(BasePage):
    # Heredamos de BasePage para reutilizar el driver

    # --- Métodos de tu código original, adaptados ---
    def open(self, url):
        logger.info(f"Abriendo URL: {url}")
        self.driver.get(url)
        self.driver.maximize_window()

    def select_language(self, lang="Español"):
        wait = WebDriverWait(self.driver, 20)
        try:
            logger.info("Esperando que el loader desaparezca.")
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.page-loader")))

            logger.info(f"Seleccionando idioma: {lang}")
            lang_dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[id^='languageListTriggerId']")))
            lang_dropdown.click()
            time.sleep(0.5)

            lang_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[@class='button_label' and normalize-space(text())='{lang}']")))
            ActionChains(self.driver).move_to_element(lang_option).pause(0.5).click().perform()
            logger.info("Idioma seleccionado con éxito.")

            logger.info("Esperando a que el loader desaparezca después de seleccionar el idioma...")
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.page-loader")))
            
        except Exception as e:
            logger.error(f"No se pudo seleccionar el idioma {lang}. Error: {e}")
            raise

    def select_pos(self, country="Colombia"):
        wait = WebDriverWait(self.driver, 20)
        try:
            logger.info(f"Seleccionando POS: {country}")
            pos_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "pointOfSaleSelectorId")))
            pos_dropdown.click()
            time.sleep(0.5)

            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".points-of-sale--opened")))
            pos_option_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[contains(@class,'points-of-sale_list_item')]//span[contains(text(), '{country}')]/..")))
            ActionChains(self.driver).move_to_element(pos_option_button).pause(0.5).click().perform()
            time.sleep(0.5)

            aplicar_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".points-of-sale_footer_action_button")))
            ActionChains(self.driver).move_to_element(aplicar_btn).pause(0.5).click().perform()
            logger.info("POS seleccionado con éxito.")

            logger.info("Esperando a que el loader desaparezca después de seleccionar el POS...")
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.page-loader")))
            # --- FIN DE LA LÍNEA CLAVE ---

        except Exception as e:
            logger.error(f"No se pudo seleccionar el POS {country}. Error: {e}")
            raise

    def select_one_way_flight(self):
        wait = WebDriverWait(self.driver, 20)
        try:
            logger.info("Seleccionando vuelo 'Solo ida'.")
            one_way_label = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='journeytypeId_1']")))
            one_way_label.click()
            logger.info("Vuelo 'Solo ida' seleccionado.")
        except Exception as e:
            logger.error(f"No se pudo seleccionar vuelo solo ida. Error: {e}")
            raise

    def select_departure_city(self, city="Bogotá"):
        wait = WebDriverWait(self.driver, 20)
        try:
            logger.info(f"Seleccionando ciudad de origen: {city}")
            departure_input = wait.until(EC.presence_of_element_located((By.ID, "departureStationInputId")))
            self.driver.execute_script("arguments[0].click();", departure_input)
            time.sleep(0.8)

            departure_input.clear()
            for char in city:
                departure_input.send_keys(char)
                time.sleep(0.15)

            option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[contains(@class,'station-control-list_item')]//button[contains(., '{city}')]")))
            ActionChains(self.driver).move_to_element(option).pause(0.5).click().perform()
            logger.info("Ciudad de origen seleccionada.")
        except Exception as e:
            logger.error(f"No se pudo seleccionar el origen {city}. Error: {e}")
            raise
    
    def select_destination_city(self, city="Cali"):
        wait = WebDriverWait(self.driver, 20)
        try:
            logger.info(f"Seleccionando ciudad de destino: {city}")
            destination_input = wait.until(EC.presence_of_element_located((By.ID, "arrivalStationInputId")))
            self.driver.execute_script("arguments[0].click();", destination_input)
            time.sleep(0.8)

            destination_input.clear()
            for char in city:
                destination_input.send_keys(char)
                time.sleep(0.15)

            option_xpath = (f"//button[contains(@class,'station-control-list_item_link')][contains(., '{city}')]")
            option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", option)
            time.sleep(0.3)
            
            ActionChains(self.driver).move_to_element(option).pause(0.5).click().perform()
            logger.info("Ciudad de destino seleccionada.")
        except Exception as e:
            logger.error(f"Error al seleccionar ciudad de destino: {e}")
            raise

    def click_search_button(self):
        wait = WebDriverWait(self.driver, 20)
        try:
            logger.info("Haciendo clic en 'Buscar'.")
            search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@id='searchButton' or contains(., 'Buscar')]")))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", search_button)
            logger.info("Clic en 'Buscar' realizado con éxito.")
        except Exception as e:
            logger.error(f"Error al hacer clic en 'Buscar': {e}")
            raise