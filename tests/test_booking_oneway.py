# tests/test_booking_oneway.py
import allure


from pages.home_page import HomePage
from pages.select_flight_page import SelectFlightPage
from pages.passengers_page import PassengersPage
from pages.services_page import ServicesPage
from pages.seatmap_page import SeatmapPage
from pages.payments_page import PaymentsPage

from utils.logger import get_logger
import time

logger = get_logger()
BASE_URL = "https://nuxqa5.avtest.ink/" 

@allure.title("Caso de Prueba 1: Reserva de Vuelo Solo Ida")
@allure.description("Este test verifica el flujo completo de una reserva de vuelo solo ida.")
def test_one_way_booking_complete(driver):
    numero_de_adultos = 1
    home = HomePage(driver)
    flight_page = SelectFlightPage(driver)
    passengers_page = PassengersPage(driver)
    services_page = ServicesPage(driver)
    seatmap_page = SeatmapPage(driver)
    payments_page = PaymentsPage(driver)

    with allure.step("Paso 1: Configurar el viaje en la Página de Inicio"):
        home.open(BASE_URL)
        home.select_language("Español")
        home.select_pos("Colombia")
        home.select_one_way_flight()
        home.select_departure_city("Bogotá")
        home.select_destination_city("Cali")
        home.click_search_button()

    with allure.step("Paso 2: Seleccionar Tarifa en la Página de Vuelos"):
        assert "/booking/select" in driver.current_url
        flight_page.select_basic_fare_and_continue()
        time.sleep(5)

    with allure.step("Paso 3: Rellenar Datos y Continuar desde la Página de Pasajeros"):
        assert "/booking/passengers" in driver.current_url
        passengers_page.fill_all_data_and_continue(num_adults=1)
        

        logger.info("Esperando a que la página de servicios cargue...")
        time.sleep(25)


    with allure.step("Paso 4: Añadir Servicios Adicionales"):
        assert "/booking/services" in driver.current_url
        services_page.add_all_available_services()
        allure.attach(driver.get_screenshot_as_png(), name="Servicios_Anadidos", attachment_type=allure.attachment_type.PNG)

    with allure.step("Paso 5: Validar Basket de Compra"):
        services_page.review_basket()
        allure.attach(driver.get_screenshot_as_png(), name="Basket_Validado", attachment_type=allure.attachment_type.PNG)



    with allure.step("Paso 5: Forzar navegación a la Página de Asientos (Seatmap)"):
        logger.info("El botón 'Continuar' de Servicios no funciona. Forzando navegación a Seatmap.")
        base_url_actual = driver.current_url.split('/booking/')[0]
        driver.get(f"{base_url_actual}/booking/seatmap")
        time.sleep(25) 

    with allure.step("Paso 5: Seleccionar Asientos en Seatmap"):
        assert "/booking/seatmap" in driver.current_url

        seatmap_page.select_seats_and_continue(num_passengers=numero_de_adultos)
    
    with allure.step("Paso 6: Realizar Pago con Tarjeta Falsa"):
        assert "/booking/payment" in driver.current_url
        payments_page.fill_payment_form_and_pay()
        allure.attach(driver.get_screenshot_as_png(), name="Datos_de_Pago_Finales", attachment_type=allure.attachment_type.PNG)
        time.sleep(5)

    

    