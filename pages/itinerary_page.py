# pages/itinerary_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.logger import get_logger
import time
import allure

logger = get_logger()

class ItineraryPage(BasePage):
    
    # --- LOCATORS ---
    PAGE_LOADER = (By.CSS_SELECTOR, "div.page-loader")
    
    # Localizador genérico para el contenedor de la página de itinerario
    ITINERARY_CONTAINER = (By.ID, "itinerary-page-container") # Reemplaza con un ID real
    
    # Localizador para encontrar los nombres de los pasajeros en el resumen
    # Busca un div que contenga el nombre y apellido
    PASSENGER_NAME_DISPLAY = lambda first, last: (By.XPATH, f"//div[contains(@class, 'passenger-name') and contains(., '{first}') and contains(., '{last}')]")
    
    # Localizador para el método de pago (Caso 2)
    PAYMENT_METHOD_DISPLAY = (By.XPATH, "//div[contains(@class, 'payment-summary-method') or contains(@class, 'payment-details')]") # Reemplaza con un localizador real

    def __init__(self, driver):
        super().__init__(driver)

    # --- ORQUESTADOR PARA CASO 1 ---
    @allure.step("Caso 1: Validar Itinerario (post-pago rechazado)")
    def validate_booking_caso1(self, passengers_data: list, base_url: str):
        """
        Orquestador principal para el Caso 1.
        Valida el itinerario después de un pago (probablemente) rechazado.
        """
        self.ensure_itinerary_page(base_url)
        self.validate_itinerary_details(passengers_data)
        self.take_screenshot("itinerario_final_caso1.png")

    # --- ORQUESTADOR PARA CASO 2 ---
    @allure.step("Caso 2: Validar Itinerario y Pago con Avianca Credits")
    def validate_booking_caso2(self, passengers_data: list, base_url: str):
        """
        Orquestador principal para el Caso 2.
        Valida el itinerario y el método de pago (Avianca Credits).
        """
        self.ensure_itinerary_page(base_url)
        self.validate_itinerary_details(passengers_data)
        self.validate_payment_with_avianca_credits()
        self.take_screenshot("itinerario_final_caso2.png")

    # --- MÉTODOS DE LÓGICA ---
    
    @allure.step("Asegurar que se está en la página de Itinerario")
    def ensure_itinerary_page(self, base_url: str):
        """
        Verifica si la URL actual es 'itinerary'. Si no (ej. atascado en 'payments' 
        por pago rechazado), fuerza la navegación a la URL del itinerario.
        [cite_start](Requisito Caso 1 [cite: 56])
        """
        wait = WebDriverWait(self.driver, 10) # Wait corto para la URL
        current_url = self.driver.current_url
        logger.info(f"URL actual: {current_url}")
        
        if "itinerary" not in current_url:
            logger.warning("No se redirigió al itinerario (probablemente pago rechazado).")
            
            # Construimos la URL del itinerario
            # Asumimos que la URL base es algo como https://nuxqaX.avtest.ink/es/booking/
            # (Si no, esta lógica debe ajustarse)
            if "payments" in current_url:
                itinerary_url = current_url.replace("payments", "itinerary")
            else:
                # Si estamos en una URL inesperada, construimos desde cero
                # (Asumiendo que el idioma 'es' está en la base_url o es fijo)
                itinerary_url = f"{base_url.rstrip('/')}/booking/itinerary" 
            
            logger.info(f"Forzando navegación a: {itinerary_url}")
            self.driver.get(itinerary_url)
            time.sleep(1) # Pausa para que la navegación se complete
        
        # Ahora que estamos (o deberíamos estar) en la página, esperamos a que cargue
        logger.info("Esperando a que la página de itinerario cargue...")
        try:
            wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER))
        except:
            pass
        wait.until(EC.visibility_of_element_located(self.ITINERARY_CONTAINER))
        logger.info("Página de itinerario cargada.")

    @allure.step("Validar información de pasajeros en el itinerario")
    def validate_itinerary_details(self, passengers_data: list):
        """
        Valida que la información de los pasajeros se muestre correctamente.
        [cite_start](Requisito Caso 1 [cite: 55] [cite_start]y Caso 2 [cite: 89])
        """
        logger.info("Validando detalles de pasajeros en el itinerario...")
        wait = WebDriverWait(self.driver, 20)
        
        for i, passenger in enumerate(passengers_data):
            first_name = passenger['first_name']
            last_name = passenger['last_name']
            logger.info(f"Buscando Pasajero {i+1}: {first_name} {last_name}")
            
            try:
                # Buscamos el localizador dinámico
                pax_locator = self.PASSENGER_NAME_DISPLAY(first_name, last_name)
                pax_element = wait.until(EC.visibility_of_element_located(pax_locator))
                
                # --- ASERCIÓN ---
                assert pax_element.is_displayed(), f"FALLO ASERCIÓN: Pasajero '{first_name} {last_name}' NO encontrado."
                logger.info(f"ASERCIÓN EXITOSA: Pasajero '{first_name} {last_name}' encontrado.")
                allure.attach(f"Pasajero {first_name} {last_name} validado.", name=f"Validación Pax {i+1}")
                
            except Exception as e:
                logger.error(f"Error validando al pasajero '{first_name} {last_name}': {e}")
                self.take_screenshot(f"error_validacion_pax_{i+1}.png")
                raise

    @allure.step("Validar que el pago se realizó con Avianca Credits")
    def validate_payment_with_avianca_credits(self):
        """
        Valida que el método de pago "Avianca credits" se muestre.
        [cite_start](Requisito Caso 2 [cite: 90])
        """
        logger.info("Validando método de pago 'Avianca credits'...")
        wait = WebDriverWait(self.driver, 20)
        
        try:
            payment_element = wait.until(EC.visibility_of_element_located(self.PAYMENT_METHOD_DISPLAY))
            payment_text = payment_element.text.lower() # Convertir a minúsculas
            
            # --- ASERCIÓN ---
            assert "avianca credits" in payment_text, f"FALLO ASERCIÓN: 'avianca credits' NO encontrado en el método de pago. Se encontró: '{payment_text}'"
            logger.info("ASERCIÓN EXITOSA: Pago con 'Avianca credits' validado.")
            allure.attach(payment_text, name="Validación Método de Pago", attachment_type=allure.attachment_type.TEXT)

        except AssertionError as e:
            logger.error(f"FALLO DE ASERCIÓN: {e}")
            self.take_screenshot("error_validacion_pago_credits.png")
            raise
        except Exception as e:
            logger.error(f"No se pudo encontrar el elemento de método de pago: {e}")
            self.take_screenshot("error_metodo_pago.png")
            raise