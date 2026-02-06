# Web Scraper de Productos – Selenium + Python

Este proyecto es un scraper automatizado desarrollado con Selenium para extraer información de productos desde el sitio de entrenamiento de Web Scraper:

https://webscraper.io/test-sites/e-commerce/allinone

El script navega por todas las categorías y subcategorías, extrae productos, limpia los datos, genera un archivo CSV y produce un análisis básico de los resultados.

---

## Características principales

- Navegación automática por categorías y subcategorías  
- Extracción de:
  - nombre  
  - precio  
  - rating  
  - número de reviews  
- Manejo de paginación  
- Limpieza y normalización de datos  
- Exportación a CSV  
- Generación de un análisis básico en `analysis.txt`  
- Manejo robusto de excepciones y logs  

---

## Requisitos

- Python 3.10+  
- Google Chrome o Microsoft Edge  
- ChromeDriver o EdgeDriver compatible  

### Dependencias Python

Instala todas las dependencias usando el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Estructura del proyecto

```
scraper.py
README.md
requirements.txt
products.csv        (generado automáticamente)
analysis.txt        (generado automáticamente)
```

---

## Cómo ejecutar el scraper

1. Clona el repositorio o copia el archivo `scraper.py`.  
2. Asegúrate de tener instalado Selenium y el driver correspondiente.  
3. Ejecuta:

```bash
python scraper.py
```

### El script realiza:

- Abre el navegador  
- Recorre todas las categorías  
- Extrae productos  
- Limpia los datos  
- Guarda `products.csv`  
- Genera `analysis.txt`  

---

## Archivos generados

### products.csv

Contiene las columnas:

| nombre | precio | rating | reviews |
|--------|---------|---------|----------|

### analysis.txt

Incluye:

- Total de productos  
- Precio promedio  
- Top 3 productos destacados  

---

## Lógica del scraper (resumen técnico)

- `init_driver()`  
  Inicializa el navegador.

- `obtener_links()`  
  Extrae todas las URLs de categorías y subcategorías desde el menú lateral.

- `obtener_productos()`  
  Extrae productos de cada página, manejando paginación.

- `refinar_data()`  
  Limpia precios y reviews, convirtiéndolos a tipos numéricos.

- `guardar_csv()`  
  Exporta los datos a un archivo CSV.

- `generar_analysis()`  
  Produce un análisis simple basado en rating, reviews y precio.

- `main()`  
  Orquesta todo el flujo.

---

## Limitaciones

- El sitio objetivo puede cambiar su estructura HTML.  
- No incluye rotación de proxies ni manejo de bloqueos.  
- No está optimizado para scraping masivo.  

---

## Contribuciones

Las mejoras son bienvenidas. Puedes abrir un issue o enviar un pull request.

---

## Licencia

Uso libre para fines educativos y de práctica.
```

---


