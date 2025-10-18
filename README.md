# Prueba Técnica - Automatización de Reserva de Vuelos

## 1. Resumen del Proyecto

Este proyecto contiene una suite de pruebas automatizadas para el **Caso de Prueba 1: Realizar booking / reserva One-way (Solo ida)** del flujo de compra de tiquetes aéreos, según los requisitos de la prueba técnica para *Test Automation Engineer*.

El script está desarrollado en **Python** utilizando el framework **Selenium WebDriver** para la interacción con el navegador y **Pytest** como motor de ejecución de pruebas. Se implementó el patrón de diseño **Page Object Model (POM)** para estructurar el código de forma modular y mantenible.

Adicionalmente, se integra con **Allure Framework** para la generación de reportes detallados y **Faker** para la creación de datos de prueba dinámicos.

---

## 2. Características Implementadas

- **Flujo de Reserva One-Way:** Automatización completa desde la página de inicio hasta la página de pagos, incluyendo:
  - Selección de idioma y POS (País).
  - Selección de ruta (origen y destino).
  - Selección de tarifa "Basic".
  - Revisión del resumen de compra.
  - Llenado de información de pasajeros de forma dinámica.
  - Llenado de datos de contacto.
  - Selección de todos los servicios adicionales disponibles.
  - Selección de asientos en el `Seatmap`.
  - Intento de pago con datos de tarjeta falsos.
- **Reportes con Allure:** El test está instrumentado con steps y títulos de Allure para una visualización clara del flujo ejecutado.
- **Capturas de Pantalla Automáticas:** El sistema toma una captura de pantalla automáticamente en el punto exacto donde una prueba falla y la adjunta al reporte de Allure.
- **Logging Detallado:** Se genera un archivo `test_run.log` con un registro de cada acción importante que realiza el script, facilitando la depuración.
- **Manejo de Datos Dinámicos:** Se utiliza `Faker` para generar nombres, apellidos, emails y datos de tarjeta, cumpliendo con el requisito de dinamismo.

---

## 3. Prerrequisitos

Asegúrate de tener los siguientes programas instalados en tu sistema:

- **Python 3.9+** y `pip`.
- **Google Chrome** (o el navegador para el que se configure el `WebDriver`).
- **ChromeDriver** compatible con tu versión de Google Chrome. Asegúrate de que el ejecutable esté en el `PATH` de tu sistema.
- **Allure Commandline**. Puedes instalarlo siguiendo las [instrucciones oficiales](https://allurereport.org/docs/gettingstarted-installation/).

---

## 4. Instrucciones de Configuración y Ejecución

Sigue estos pasos para configurar y ejecutar el proyecto en tu máquina local.

### **Paso 1: Clonar el Repositorio**

```bash
git clone https://github.com/ingcristiangarcas/prueba_automatizacion_QA.git
cd flyr_test_project
```

### **Paso 2: Crear y Activar un Entorno Virtual**

Es una buena práctica aislar las dependencias del proyecto.

```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
.\venv\Scripts\activate
# En macOS / Linux:
# source venv/bin/activate
```

### **Paso 3: Instalar las Dependencias**

Con el entorno virtual activado, instala todas las librerías necesarias.

```bash
pip install -r requirements.txt
```

---

## 5. Cómo Ejecutar las Pruebas

Para correr la suite de pruebas y generar los resultados para Allure, ejecuta el siguiente comando desde la raíz del proyecto (`flyr_test_project/`):

```bash
pytest --alluredir=./allure-results --clean-alluredir
```

- `--alluredir=./allure-results`: Especifica la carpeta donde se guardarán los datos del reporte.
- `--clean-alluredir`: Limpia los resultados de ejecuciones anteriores para tener un reporte fresco.

---

## 6. Cómo Visualizar el Reporte de Pruebas

Una vez que la ejecución del test haya finalizado, ejecuta el siguiente comando para generar y abrir el reporte web de Allure:

```bash
allure serve ./allure-results
```

Este comando abrirá una nueva pestaña en tu navegador con el reporte detallado, donde podrás ver cada paso, las capturas de pantalla, tiempos de ejecución y el resultado final.
