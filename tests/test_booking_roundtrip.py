import pytest
import allure
import time
from pages_roundtrip.offers_page import OffersPage 
from pages_roundtrip.select_flight_page_rt import SelectFlightPageRT
from pages_roundtrip.passenger_page_rt import PassengersPageRT
from pages_roundtrip.services_page_rt import ServicesPageRT
from utils.test_data_generator import generate_passenger_data_for_roundtrip


# ...
OFFERS_URL_SUFFIX = "/es/ofertas-destinos/ofertas-de-vuelos"
# --- DATOS PARA EDICIÓN ---
EDIT_ORIGIN_CODE = "MGA" 
EDIT_DEST_CODE = "MDE"   
# --- NUEVO: Fechas de Edición ---
EDIT_DEP_DAY = "20"
EDIT_DEP_MONTH = "11" # Noviembre
EDIT_DEP_YEAR = "2025"
# (Dejamos las de regreso para después)
EDIT_RET_DAY = "30"
EDIT_RET_MONTH = "11" 
EDIT_RET_YEAR = "2025"
MAX_PASSENGERS = 9 # Lo usaremos después
# ... (VOUCHER, PIN) ...

@allure.feature("Booking")
@allure.story("Realizar reserva Round-trip (Ida y vuelta) [Caso 2]")
class TestRoundTripBooking:

    @allure.title("Caso Automatizado 2: [DEBUG] Verificar navegación Ofertas -> Select Flight")
    def test_complete_roundtrip_booking(self, driver, base_url, logger):
        
        start_time = time.time()
        status = "FAIL" 
        
        try:
            # --- 1. Navegar a Ofertas ---
            offers_url = base_url.rstrip('/') + OFFERS_URL_SUFFIX
            with allure.step(f"Paso 1: Navegar a la página de Ofertas: {offers_url}"):
                driver.get(offers_url)
                logger.info(f"Iniciando Caso 2 desde URL de Ofertas: {offers_url}")
                allure.attach(driver.get_screenshot_as_png(), name="Pagina_Ofertas", attachment_type=allure.attachment_type.PNG)

            # --- 2. Seleccionar Oferta y Buscar (Valores por defecto) ---
            offers_page = OffersPage(driver)
            with allure.step(f"Paso 2: Seleccionar oferta y Buscar (Defaults)"):
                offers_page.select_offer_and_search_defaults() # <-- LLAMAMOS AL MÉTODO SIMPLE
                logger.info("Búsqueda simple iniciada. Deberíamos estar en 'Select Flight'.")
                allure.attach(driver.get_screenshot_as_png(), name="Pagina_Select_Flight_Esperada", attachment_type=allure.attachment_type.PNG)
                # Añadimos una pausa larga al final para que puedas VER la página
                logger.info("Pausa de 10 segundos para verificación visual...")
                time.sleep(10) 
            
            # --- 3. Hacer Clic en Editar ---
            select_flight_rt = SelectFlightPageRT(driver) 
            with allure.step(f"Paso 3: Abrir Editar y cambiar Origen/Destino/Fechas/Pasajeros"):
                select_flight_rt.click_edit_booking_button() # Abre el modal
                
                select_flight_rt.edit_origin_to_managua() 
                select_flight_rt.edit_destination_to_medellin()
                select_flight_rt.edit_departure_date(EDIT_DEP_DAY, EDIT_DEP_MONTH, EDIT_DEP_YEAR)
                select_flight_rt.edit_return_date(EDIT_RET_DAY, EDIT_RET_MONTH, EDIT_RET_YEAR)
                
                # --- CAMBIAMOS PASAJEROS ---
                select_flight_rt.edit_passengers_to_max(MAX_PASSENGERS)
                # ---
                logger.info("Modal editado. Aplicando búsqueda...")
                allure.attach(driver.get_screenshot_as_png(), name="Modal_Editado_Completo", attachment_type=allure.attachment_type.PNG)
                
                # --- CLIC EN BUSCAR ---
                select_flight_rt.click_apply_search()
                logger.info("Página recargada con la nueva búsqueda de 9 pasajeros.")
                
                logger.info("Origen, Destino, Fechas y Pasajeros cambiados. Modal debería seguir abierto.")
                allure.attach(driver.get_screenshot_as_png(), name="Modal_Editado_Completo", attachment_type=allure.attachment_type.PNG)
                logger.info("Pausa de 10 segundos para verificación visual...")
                time.sleep(10)
            
            # --- 4. Seleccionar Tarifa de IDA ---
            with allure.step("Paso 4: Seleccionar tarifa de IDA"):
                select_flight_rt.select_departure_fare() # <-- LLAMAMOS AL NUEVO MÉTODO
                select_flight_rt.select_return_fare()
                logger.info("Tarifa de IDA seleccionada.")
                allure.attach(driver.get_screenshot_as_png(), name="Tarifa_Ida_Seleccionada", attachment_type=allure.attachment_type.PNG)
                # --- VALIDAR Y CONTINUAR ---
                select_flight_rt.validate_summary()
                select_flight_rt.click_continue_to_passengers()
                # ---
                logger.info("Pausa de 10 segundos para verificación visual...")
                time.sleep(10)
                logger.info("Navegando a la página de Pasajeros.")

            # --- 5. Passengers Page (¡AHORA ACTIVO!) ---
            passengers_page = PassengersPageRT(driver)
            with allure.step(f"Paso 5: Ingresar {MAX_PASSENGERS} pasajeros (1ro='Test Test')"):
                # Generamos los 9 pasajeros (con 'Test Test' primero)
                passengers_data = generate_passenger_data_for_roundtrip(MAX_PASSENGERS)
                # Llamamos al método que rellena todos los formularios y da clic en continuar
                passengers_page.fill_all_passenger_data(passengers_data)
                
                logger.info("Página de Pasajeros (Nombres/Apellidos) completada.")
                allure.attach(driver.get_screenshot_as_png(), name="Pasajeros_Nombres_Completados", attachment_type=allure.attachment_type.PNG)
                
                # El time.sleep(10) ya está dentro del método fill_all_names_and_lastnames
                # Así que esta pausa es opcional, pero la dejamos por si acaso.
                time.sleep(5)

                # --- 6. Services Page ---
            services_page = ServicesPageRT(driver) # 1. Instancia la nueva página
            with allure.step("Paso 6: Añadir equipaje normal y deportivo para todos los pasajeros"):
                
                services_page.wait_for_page_to_load() # 2. Espera a que cargue
                
                services_page.add_all_baggage_services() # 3. Añade todo el equipaje
                
                services_page.validate_services_in_basket() # 4. Valida en el basket
                
                logger.info("Página de Servicios completada.")
                allure.attach(driver.get_screenshot_as_png(), name="Servicios_Completados", attachment_type=allure.attachment_type.PNG)
                
                services_page.click_continue() # 5. Continúa a la siguiente página (Seatmap)
            
            # <<< --- FIN DE LO NUEVO --- >>>
            

            status = "PASS" # Si llega aquí, la navegación funcionó
            logger.info("¡[DEBUG] Navegación Ofertas -> Select Flight exitosa!")

        except Exception as e:
            status = "FAIL"
            logger.error(f"[DEBUG] Test Falló: {e}", exc_info=True)
            allure.attach(driver.get_screenshot_as_png(), name="FALLO_CAPTURA_FINAL", attachment_type=allure.attachment_type.PNG)
            raise e
        
        finally:
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)
            logger.info(f"[DEBUG] Resultado: {status} en {elapsed_time}s")