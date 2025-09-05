#!/usr/bin/env python3
"""
Scraper alternativo usando Selenium para sitios que requieren JavaScript
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JumboSeleniumScraper:
    """Scraper usando Selenium para contenido dinámico"""

    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Configura el driver de Chrome"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def extract_filter_titles_selenium(self, url, category_name):
        """Extrae títulos de filtros usando Selenium"""
        try:
            logger.info(f"Procesando con Selenium: {category_name}")
            self.driver.get(url)

            # Esperar a que cargue la página
            time.sleep(3)

            # Buscar el contenedor de filtros
            filter_selectors = [
                ".filters",
                ".filter-sidebar",
                ".left-filters",
                ".sidebar",
                ".filter-container",
                "[data-testid*='filter']",
                "[class*='filter']"
            ]

            filter_container = None
            for selector in filter_selectors:
                try:
                    filter_container = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Contenedor encontrado con selector: {selector}")
                    break
                except TimeoutException:
                    continue

            if filter_container:
                # Extraer títulos de secciones
                title_elements = filter_container.find_elements(By.CSS_SELECTOR, "h3, h4, h5, h6, div, span, label")

                section_titles = []
                for elem in title_elements:
                    text = elem.text.strip()
                    if text and 3 <= len(text) <= 40:
                        if not text[0].isdigit() and not text.startswith(('+', '-')):
                            section_titles.append(text)

                # Filtrar y limpiar títulos
                seen = set()
                unique_titles = []
                for title in section_titles:
                    title_lower = title.lower()
                    if title_lower not in seen:
                        unique_titles.append(title)
                        seen.add(title_lower)

                # Filtrar títulos válidos
                filter_section_titles = []
                for title in unique_titles:
                    title_lower = title.lower()
                    if any(keyword in title_lower for keyword in [
                        'categoría', 'subcategoría', 'marca', 'precio', 'tipo', 'color',
                        'tamaño', 'capacidad', 'peso', 'voltaje', 'potencia'
                    ]) or len(title.split()) <= 4:
                        if not re.search(r'\d+(\s*(kg|l|ml|cm|w|hz|rpm))', title_lower):
                            filter_section_titles.append(title)

                return filter_section_titles[:20]

            else:
                logger.warning(f"No se encontró contenedor de filtros para {category_name}")
                return []

        except Exception as e:
            logger.error(f"Error con Selenium en {category_name}: {str(e)}")
            return []

    def scrape_category_selenium(self, category_name, url):
        """Scrape una categoría específica con Selenium"""
        if not self.driver:
            self.setup_driver()

        filters = self.extract_filter_titles_selenium(url, category_name)
        return {
            'url': url,
            'filters': filters,
            'total_filters': len(filters)
        }

    def close_driver(self):
        """Cierra el driver de Selenium"""
        if self.driver:
            self.driver.quit()
            self.driver = None

def main():
    """Función principal para testing"""
    scraper = JumboSeleniumScraper()

    try:
        # Probar con una categoría
        result = scraper.scrape_category_selenium(
            "Electro",
            "https://www.jumbo.com.ar/electro"
        )

        print(f"Resultado para Electro: {result['total_filters']} filtros")
        for filter_name in result['filters'][:10]:
            print(f"  - {filter_name}")

    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()
