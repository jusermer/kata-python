import csv
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException
)

# deivers funcionamiento
BASE_URL = "https://webscraper.io/test-sites/e-commerce/allinone"
TIEMPO_ESPERA = 10
ESPERA_CARGA = 2

# Logs exepciones
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Inicialización del navegador
# ---------------------------------------------------------
def init_driver():
    """
    Inicializa el navegador Chrome.
    """
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver


# ---------------------------------------------------------
# Obtención de categorías y subcategorías
# ---------------------------------------------------------
def obtener_links(driver):
    """
    Recorre el menú lateral y obtiene todas las URLs de categorías
    y subcategorías. Se guardan solo los href para evitar problemas
    de referencias obsoletas cuando la página cambia.
    """
    wait = WebDriverWait(driver, TIEMPO_ESPERA)

    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#side-menu a")))
    categorias = driver.find_elements(By.CSS_SELECTOR, "#side-menu a")

    urls_principales = [c.get_attribute("href") for c in categorias]
    urls_finales = []

    # Navegar a cada categoría para obtener subcategorías
    for url in urls_principales:
        urls_finales.append(url)

        driver.get(url)
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "thumbnail"))) 

        # Subcategorías visibles solo después de entrar a la categoría
        subcategorias = driver.find_elements(By.CSS_SELECTOR, ".subcategory-link, .category-link")

        for sub in subcategorias:
            sub_href = sub.get_attribute("href")
            if sub_href and "allinone" in sub_href:
                urls_finales.append(sub_href)

    # Eliminar duplicados manteniendo el orden original
    return list(dict.fromkeys(urls_finales))


# ---------------------------------------------------------
# Extracción de productos
# ---------------------------------------------------------
def obtener_productos(driver):
    """
    Extrae los productos de la categoría actual.
    Si existe paginación, avanza hasta la última página.
    """
    wait = WebDriverWait(driver, TIEMPO_ESPERA)
    productos = []

    while True:
        try:
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "thumbnail")))
        except TimeoutException:
            logger.warning("No se encontraron productos en la página")
            break

        items = driver.find_elements(By.CLASS_NAME, "thumbnail")

        for item in items:

            # Extraer datos del producto
            nombre = item.find_element(By.CLASS_NAME, "title").text.strip()
            precio = item.find_element(By.CLASS_NAME, "price").text.strip()
            try:
                rating_raw = item.find_element(By.CSS_SELECTOR, "p[data-rating]").get_attribute("data-rating")
            except NoSuchElementException:
                rating_raw = "0"

            rating = int(rating_raw) if rating_raw else 0

            reviews = item.find_element(By.CLASS_NAME, "review-count").text.strip()

            #agregar a la lista de productos
            productos.append({
                "nombre": nombre,
                "precio": precio,
                "rating": rating,
                "reviews": reviews
            })

        # Intentar avanzar en la paginación
        try:
            paginacion = driver.find_element(By.CSS_SELECTOR, "ul.pagination")
        except NoSuchElementException:
            # No hay paginación en esta categoría
            break

        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "ul.pagination li:last-child a")
        except NoSuchElementException:
            break

        # Si el botón está deshabilitado, ya estamos en la última página
        if "disabled" in next_btn.get_attribute("class"):
            break

        try:
            next_btn.click()
        except (StaleElementReferenceException, ElementClickInterceptedException, WebDriverException):
            logger.warning("Fallo al hacer click en el botón de siguiente, reintentando...")
            wait.until(EC.staleness_of(next_btn))
            continue

        # Esperar a que la página cargue nuevos productos
        try:
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "thumbnail")))
        except TimeoutException:
            logger.warning("Timeout esperando nuevos productos después de paginación")
            break

    return productos


# ---------------------------------------------------------
# Limpieza y parseo de datos
# ---------------------------------------------------------
def refinar_data(productos):
    """
    Limpia y convierte los valores de precio y reviews a tipos numéricos.
    Consolida el parseo en una sola función para mayor organización.
    """
    if not productos:
        logger.warning("Lista de productos vacía")
        return []

    datos_limpios = []
    for p in productos:
        try:
            precio = float(p["precio"].replace("$", ""))
        except (ValueError, AttributeError):
            logger.warning(f"No se pudo parsear precio: {p['precio']}")
            precio = 0.0

        try:
            reviews = int(p["reviews"].replace(" reviews", "").strip())
        except (ValueError, AttributeError):
            logger.warning(f"No se pudo parsear reviews: {p['reviews']}")
            reviews = 0

        datos_limpios.append({
            "nombre": p["nombre"],
            "precio": precio,
            "rating": p["rating"],
            "reviews": reviews
        })

    return datos_limpios


# ---------------------------------------------------------
# Guardado de CSV
# ---------------------------------------------------------
def guardar_csv(productos):
    """
    Guarda los productos en un archivo CSV.
    Si el archivo está en uso (Excel abierto), se renombra automáticamente.
    """
    filename = "products.csv"
    fieldnames = ["nombre", "precio", "rating", "reviews"]

    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(productos)
        logger.info(f"CSV guardado en: {filename}")
    except PermissionError:
        logger.warning(f"{filename} está en uso. Usando nombre alternativo...")
        filename = "products_output.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(productos)
        logger.info(f"CSV guardado en: {filename}")


# ---------------------------------------------------------
# Análisis básico
# ---------------------------------------------------------
def generar_analysis(productos):
    """
    Genera un análisis simple basado en:
    - rating
    - reviews
    - precio (como tercer criterio de desempate)
    """
    if not productos:
        logger.warning("No hay productos para analizar")
        return

    total = len(productos)
    precio_promedio = sum(p["precio"] for p in productos) / total

    top3 = sorted(
        productos,
        key=lambda x: (x["rating"], x["reviews"], x["precio"]),
        reverse=True
    )[:3]

    with open("analysis.txt", "w", encoding="utf-8") as f:
        f.write(f"Total de productos: {total}\n")
        f.write(f"Precio promedio: ${precio_promedio:.2f}\n")
        f.write("Top 3 productos destacados:\n")
        for p in top3:
            f.write(f"- {p['nombre']} | {p['rating']}⭐ | {p['reviews']} reviews | ${p['precio']:.2f}\n")
    
    logger.info("Análisis generado en analysis.txt")


# ---------------------------------------------------------
# Flujo principal
# ---------------------------------------------------------
def main():
    driver = init_driver()
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, TIEMPO_ESPERA)

    productos_totales = []

    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#side-menu a")))
        enlaces = obtener_links(driver)
        logger.info(f"Se encontraron {len(enlaces)} categorías/subcategorías")

        for i, url in enumerate(enlaces, 1):
            logger.info(f"[{i}/{len(enlaces)}] Extrayendo: {url}")
            driver.get(url)
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "thumbnail")))

            productos = obtener_productos(driver)
            productos_totales.extend(productos)
            logger.info(f"  → {len(productos)} productos extraídos de esta categoría")

        logger.info(f"Total de productos extraídos: {len(productos_totales)}")
        
        if productos_totales:
            datos_limpios = refinar_data(productos_totales)
            guardar_csv(datos_limpios)
            generar_analysis(datos_limpios)
            logger.info("Scraping completado exitosamente")
        else:
            logger.warning("No se extrajeron productos")

    except Exception as e:
        logger.error(f"Error durante scraping: {str(e)}", exc_info=True)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()