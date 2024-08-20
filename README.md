# Web Scraper

Este repositorio contiene un script en Python para realizar scraping de datos de un sitio web utilizando Selenium y BeautifulSoup. Los datos extraídos se almacenan en archivos JSON.

## Requisitos

Antes de ejecutar el script, asegúrate de tener instaladas las siguientes dependencias:

- Python 3.x
- Selenium
- BeautifulSoup4
- Requests
- json

Puedes instalarlas utilizando pip:

```bash
pip install -r requirements.txt
```

## Configuración

1. **Instalar Google Chrome y ChromeDriver:**

   - Asegúrate de tener Google Chrome instalado en tu sistema.
   - Descarga la versión correspondiente de ChromeDriver desde [aquí](https://sites.google.com/a/chromium.org/chromedriver/downloads).
   - Asegúrate de que el ejecutable de ChromeDriver esté en tu PATH o en la misma carpeta que el script.

2. **Configurar WebDriver:**

   En el script `main.py`, asegúrate de que el `webdriver.Chrome()` esté configurado correctamente con la ruta del ChromeDriver si no está en el PATH.

3. **Modificar el URL objetivo (opcional):**

   Si deseas realizar scraping en un sitio web diferente, actualiza la URL en el script `main.py`.

## Ejecución

Para ejecutar el script de scraping, utiliza el siguiente comando en tu terminal:

```bash
python main.py
```

## Modo de Ejecución
El script puede correr en varios modos, dependiendo de las opciones que pases:

Scraping Completo: Ejecuta el scraping y guarda los datos en archivos JSON:

```bash
python main.py
```

Evitar Scraping y Procesar Datos Existentes: Si deseas omitir el proceso de scraping y trabajar directamente con los datos existentes, utiliza la opción --skip-scraping:

```bash
python main.py --skip-scraping
```
