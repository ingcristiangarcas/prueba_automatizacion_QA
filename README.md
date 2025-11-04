Prueba Técnica - Automatización de Reserva de Vuelos

1. Resumen del Proyecto

Este proyecto contiene una suite de pruebas automatizadas para dos casos de prueba principales: el Caso 1 (Reserva One-way) y el Caso 2 (Reserva Round-trip) del flujo de compra de tiquetes aéreos, según los requisitos de la prueba técnica.

El script está desarrollado en Python utilizando el framework Selenium WebDriver para la interacción con el navegador y Pytest como motor de ejecución de pruebas. Se implementó el patrón de diseño Page Object Model (POM) para estructurar el código de forma modular y mantenible.

Adicionalmente, se integra con Allure Framework para la generación de reportes detallados y Faker para la creación de datos de prueba dinámicos.

2. Casos de Prueba Implementados

Caso 1: Realizar booking / reserva One-way (Solo ida)

Flujo de Reserva One-Way: Automatización completa desde la página de inicio hasta la página de pagos, incluyendo:

Selección de idioma y POS (País).

Selección de ruta (origen y destino).

Selección de tarifa "Basic".

Revisión del resumen de compra.

Llenado de información de pasajeros de forma dinámica.

Llenado de datos de contacto.

Selección de todos los servicios adicionales disponibles.

Selección de asientos en el Seatmap.

Intento de pago con datos de tarjeta falsos.

Caso 2: Realizar booking / reserva Round-trip (Ida y Vuelta)

Este es un test de regresión end-to-end (E2E) que valida un flujo de reserva complejo de ida y vuelta (test_booking_roundtrip.py).

Pasos del Flujo:

Navegación: Abre la página de Ofertas.

Búsqueda Inicial: Selecciona una oferta y busca con valores por defecto.

Edición de Vuelo: En la página de Select Flight, abre el modal de "Editar" y cambia:

Origen y Destino.

Fechas de Ida y Vuelta.

Número de pasajeros (ej. 9 pasajeros).

Selección de Tarifas: Selecciona las tarifas para los vuelos de ida y vuelta.

Datos de Pasajeros: Llena los datos para todos los pasajeros.

Servicios Adicionales: Añade equipaje para los pasajeros en la página de Services.

Mapa de Asientos: Selecciona asientos para los pasajeros.

Flujo de Pago (Avianca Credits):

Navega a la página de Payment.

Activa el pago con "Avianca Credits".

Ingresa un número de Voucher y un PIN.

Aplica el crédito y confirma el pago.

3. Prerrequisitos

Asegúrate de tener los siguientes programas instalados en tu sistema:

Python 3.9+ y pip.

Google Chrome (o el navegador para el que se configure el WebDriver).

ChromeDriver compatible con tu versión de Google Chrome. Asegúrate de que el ejecutable esté en el PATH de tu sistema.

Allure Commandline. Puedes instalarlo siguiendo las instrucciones oficiales.

4. Instrucciones de Configuración y Ejecución

Sigue estos pasos para configurar y ejecutar el proyecto en tu máquina local.

Paso 1: Clonar el Repositorio

git clone [https://github.com/ingcristiangarcas/prueba_automatizacion_QA.git](https://github.com/ingcristiangarcas/prueba_automatizacion_QA.git)
cd flyr_test_project


Paso 2: Crear y Activar un Entorno Virtual

Es una buena práctica aislar las dependencias del proyecto.

# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
.\venv\Scripts\activate
# En macOS / Linux:
# source venv/bin/activate


Paso 3: Instalar las Dependencias

Con el entorno virtual activado, instala todas las librerías necesarias.

pip install -r requirements.txt


5. Cómo Ejecutar las Pruebas

Para correr la suite de pruebas y generar los resultados para Allure, ejecuta el siguiente comando desde la raíz del proyecto (flyr_test_project/):

# Para ejecutar la suite completa (ambos casos)
pytest --alluredir=./allure-results --clean-alluredir


--alluredir=./allure-results: Especifica la carpeta donde se guardarán los datos del reporte.

--clean-alluredir: Limpia los resultados de ejecuciones anteriores para tener un reporte fresco.

Ejecutar un Caso Específico

Si solo deseas ejecutar el Caso 2 (Round-trip):

pytest tests/test_booking_roundtrip.py --alluredir=./allure-results --clean-alluredir


6. Cómo Visualizar el Reporte de Pruebas

Una vez que la ejecución del test haya finalizado, ejecuta el siguiente comando para generar y abrir el reporte web de Allure:

allure serve ./allure-results


Este comando abrirá una nueva pestaña en tu navegador con el reporte detallado, donde podrás ver cada paso, las capturas de pantalla, tiempos de ejecución y el resultado final.

7. Desafíos de Automatización y Soluciones (Caso 2)

Durante la implementación del Caso 2, se encontraron varios desafíos significativos, principalmente en la página de Pagos.

1. El Velo de Carga (page-loader)

Problema: La aplicación utiliza un overlay (velo) de carga (ej. <div class="page-loader">...</div>) cada vez que procesa información (al cargar la página, al aplicar un voucher, etc.).

Síntoma:

ElementClickInterceptedException: El overlay estaba físicamente encima del elemento en el que queríamos hacer clic. (Visto en nuxqa5).

TimeoutException: Nuestra espera EC.element_to_be_clickable() fallaba porque el elemento, aunque presente, estaba tapado por el overlay y, por lo tanto, no era "clickeable". (Visto en nuxqa4).

Solución: Se implementó una "espera de robustez". Antes de interactuar con cualquier elemento clave, se añadió una espera explícita para que el overlay desapareciera:

wait.until(EC.invisibility_of_element_located(self.PAGE_LOADER_PAGOS))


2. El "Switch" de Pago (Clic Forzado)

Problema: El switch (checkbox) para "Avianca Credits" presentaba dos problemas:

El <input> real estaba visualmente oculto o era difícil de interactuar con él.

Incluso apuntando al elemento correcto, el overlay de carga (page-loader) interfería y causaba un TimeoutException.

Solución (Clic Forzado con JavaScript):
Para garantizar que el clic se realizara sin importar si el elemento estaba tapado o no (dado que era un test temporal), se implementó un clic forzado usando JavaScript.

Se utilizó un XPath absoluto (proveído para este test temporal) para localizar el <input>.

Se esperó solo a que el elemento estuviera presente en el DOM (EC.presence_of_element_located), no "clickeable".

Se ejecutó el clic directamente en el DOM usando execute_script, ignorando todos los bloqueos:

# Espera que exista
credits_cb = wait.until(EC.presence_of_element_located(self.AVIANCA_CREDITS_CHECKBOX))

# ¡Forzar el clic!
self.driver.execute_script("arguments[0].click();", credits_cb)


3. Error de Configuración de Entorno (nuxqa5)

Observación: Durante las pruebas en nuxqa5, se detectó un popup de error con el mensaje: ConfigurationErrorsException en la página de Asientos.

Diagnóstico: Esto no es un error del script de automatización. Es un error del backend o de la configuración del entorno nuxqa5, que indica que el servidor no pudo procesar la solicitud del mapa de asientos.