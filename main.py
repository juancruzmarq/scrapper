import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests
import os
import json
import logging
from urls import URL_TEST

# Configuraciones globales
CONFIG = {
    "URL_BASE": "https://www.snusfarmer.com/es",
    "output_folder": "jsons",
    "url_list_file": "jsons.txt",
    "csv_file": "./data/products.csv",
    "headless_browser": False,
    "log_file": "scraper.log"
}

# Configuración del logging
logging.basicConfig(filename=CONFIG["log_file"], level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_driver(headless=True):
    options = Options()
    options.headless = headless
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def extract_product_urls(driver, seen_urls):
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_divs = soup.find_all('div', class_='product-inner border-allways')
        logging.info(f"Se encontraron {len(product_divs)} productos en la página")
        
        for product in product_divs:
            product_url = product.find('a', class_='title title-font')['href']
            full_url = CONFIG["URL_BASE"] + product_url + '?format=json'
            seen_urls.add(full_url)
    except Exception as e:
        logging.error(f"Error al extraer URLs de productos: {e}")

def scrape_product_urls(driver, urls_to_scrape):
    seen_urls = set()

    for url in urls_to_scrape:
        try:
            logging.info(f"Procesando URL: {CONFIG['URL_BASE'] + url}")
            driver.get(CONFIG["URL_BASE"] + url)
            extract_product_urls(driver, seen_urls)
        except Exception as e:
            logging.error(f"Error al procesar {url}: {e}")

    return seen_urls

def write_urls_to_file(urls, filename):
    try:
        with open(filename, 'w') as file:
            for url in urls:
                file.write(f"{url}\n")
        logging.info(f"URLs guardadas en {filename}")
    except Exception as e:
        logging.error(f"Error al escribir URLs en archivo: {e}")

def read_urls_from_file(filename):
    if not os.path.exists(filename):
        logging.warning(f"El archivo {filename} no existe")
        return set()

    try:
        with open(filename, 'r') as file:
            logging.info(f"Leyendo URLs de {filename}")
            return set(file.read().splitlines())
    except Exception as e:
        logging.error(f"Error al leer el archivo {filename}: {e}")
        return set()

def fetch_and_save_json(url, folder):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            product_id = data['product']['id']
            name = url.split('/')[-1].split('?')[0].split('.')[0]
            file_path = os.path.join(folder, f"{product_id}_{name}.json")
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            logging.info(f"Guardado: {file_path}")
        else:
            logging.error(f"Error al obtener datos de {url}: {response.status_code}")
    except Exception as e:
        logging.error(f"Error al guardar JSON de {url}: {e}")

def check_file_exists(url, folder):
    try:
        name = url.split('/')[-1].split('?')[0].split('.')[0]
        return any(name in file for file in os.listdir(folder))
    except Exception as e:
        logging.error(f"Error al verificar si el archivo existe: {e}")
        return False

def get_product_data(json_data):
    try:
        product = json_data['product']
        product_data = {
            'product_id': product['id'],
            'name': product['title'],
            'weight': product['weight'],
            'description': product['description'],
            'available': product['stock']['available'],
            'brand_name': product['brand']['title'] if product['brand'] else None,
            'price': product['price']['price'],
            'currency': json_data['gtag']['events']['view_item']['currency'],
            'item_category': json_data['gtag']['events']['view_item']['items'][0]['item_category'],
            'tax': product['tax'],
            'sku': product['sku'],
            'variant': product['variant']
        }
        return product_data
    except KeyError as e:
        logging.error(f"Error al extraer datos del producto: clave no encontrada {e}")
        return None
    except Exception as e:
        logging.error(f"Error al extraer datos del producto: {e}")
        return None

def save_products_to_csv(products_data, filename):
    try:
        with open(filename, 'w', encoding='utf8') as file:
            file.write("product_id,name,weight,description,available,brand_name,price,currency,item_category,tax,sku,variant\n")
            for product in products_data:
                if product:
                    file.write(f"{product['product_id']},{product['name']},{product['weight']},{product['description']},{product['available']},{product['brand_name']},{product['price']},{product['currency']},{product['item_category']},{product['tax']},{product['sku']},{product['variant']}\n")
        logging.info(f"Datos guardados en {filename}")
    except Exception as e:
        logging.error(f"Error al guardar datos en CSV: {e}")

def main(skip_scraping):
    if not skip_scraping:
        driver = get_driver(headless=CONFIG["headless_browser"])

        # Scrape URLs
        urls_to_scrape = URL_TEST  # Asegúrate de definir URL_TEST adecuadamente
        seen_urls = scrape_product_urls(driver, urls_to_scrape)
        driver.quit()

        # Write URLs to file
        existing_urls = read_urls_from_file(CONFIG["url_list_file"])
        all_urls = seen_urls.union(existing_urls)
        write_urls_to_file(all_urls, CONFIG["url_list_file"])

        # Fetch and save JSON data
        os.makedirs(CONFIG["output_folder"], exist_ok=True)
        for url in all_urls:
            if not check_file_exists(url, CONFIG["output_folder"]):
                fetch_and_save_json(url, CONFIG["output_folder"])
            else:
                logging.info(f"El archivo {url} ya existe")
    else:
        logging.info("Skipping scraping as per the command line argument.")

    # Read JSON data and process
    products_data = []
    for file in os.listdir(CONFIG["output_folder"]):
        with open(os.path.join(CONFIG["output_folder"], file), 'r') as json_file:
            data = json.load(json_file)
            product_data = get_product_data(data)
            if product_data:
                products_data.append(product_data)

    # Save products data to CSV
    save_products_to_csv(products_data, CONFIG["csv_file"])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape products and save data.')
    parser.add_argument('--skip-scraping', action='store_true', help='Skip the scraping process and use existing data.')
    args = parser.parse_args()

    main(skip_scraping=args.skip_scraping)
