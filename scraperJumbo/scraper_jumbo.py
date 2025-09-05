#!/usr/bin/env python3
"""
Scraper para extraer filtros de categorías de Jumbo
Extrae los títulos de las secciones de filtros del menú lateral izquierdo
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JumboScraper:
    """Clase para scrapear filtros de Jumbo"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Definir categorías y URLs
        self.categories = [
            ('Electro', 'https://www.jumbo.com.ar/electro'),
            ('Hogar', 'https://www.jumbo.com.ar/hogar-y-textil'),
            ('Tiempo Libre', 'https://www.jumbo.com.ar/tiempo-libre'),
            ('Bebés y Niños', 'https://www.jumbo.com.ar/bebes-y-ninos'),
            ('Almacén', 'https://www.jumbo.com.ar/almacen'),
            ('Bebidas', 'https://www.jumbo.com.ar/bebidas'),
            ('Frutas y Verduras', 'https://www.jumbo.com.ar/frutas-y-verduras'),
            ('Carnes', 'https://www.jumbo.com.ar/carnes'),
            ('Pescados y Mariscos', 'https://www.jumbo.com.ar/pescados-y-mariscos'),
            ('Quesos y Fiambres', 'https://www.jumbo.com.ar/quesos-y-fiambres'),
            ('Lácteos', 'https://www.jumbo.com.ar/lacteos'),
            ('Congelados', 'https://www.jumbo.com.ar/congelados'),
            ('Panadería y Pastelería', 'https://www.jumbo.com.ar/panaderia-y-pastelería'),
            ('Pastas Frescas', 'https://www.jumbo.com.ar/pastas-frescas'),
            ('Rotisería', 'https://www.jumbo.com.ar/Rotisería'),
            ('Perfumería', 'https://www.jumbo.com.ar/perfumeria'),
            ('Limpieza', 'https://www.jumbo.com.ar/limpieza'),
            ('Mascotas', 'https://www.jumbo.com.ar/mascotas')
        ]

    def extract_filter_titles(self, url, category_name):
        """Extrae los títulos de las secciones de filtros de una categoría"""
        try:
            logger.info(f"Procesando categoría: {category_name}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            # Forzar encoding UTF-8
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')

            # Buscar el contenedor principal de filtros
            filter_container = None

            # Buscar posibles contenedores de filtros
            possible_selectors = [
                '.filters',
                '.filter-sidebar',
                '.left-filters',
                '.sidebar',
                '.filter-container',
                '.facets',
                '.filter-menu',
                '.filter-list'
            ]

            for selector in possible_selectors:
                container = soup.select_one(selector)
                if container:
                    filter_container = container
                    logger.debug(f"Contenedor encontrado con selector: {selector}")
                    break

            if not filter_container:
                # Buscar por clase que contenga 'filter'
                filter_elements = soup.find_all(class_=re.compile(r'filter'))
                if filter_elements:
                    filter_container = max(filter_elements, key=lambda x: len(x.get_text()))
                    logger.debug("Contenedor encontrado por clase que contiene 'filter'")

            if filter_container:
                # Extraer títulos de secciones
                section_titles = []

                # Buscar todos los elementos de título dentro del contenedor
                title_elements = filter_container.find_all(['h3', 'h4', 'h5', 'h6', 'div', 'span', 'label'])

                for elem in title_elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 2 and len(text) < 40:
                        # Verificar que sea un título de sección válido
                        if not text[0].isdigit() and not text.startswith(('+', '-')):
                            # Limpiar texto preservando caracteres especiales
                            clean_text = text.strip()
                            if clean_text and len(clean_text.split()) <= 5:
                                section_titles.append(clean_text)

                # Eliminar duplicados manteniendo orden
                seen = set()
                unique_titles = []
                for title in section_titles:
                    title_lower = title.lower()
                    if title_lower not in seen:
                        unique_titles.append(title)
                        seen.add(title_lower)

                # Filtrar títulos que sean claramente secciones de filtros
                filter_section_titles = []
                valid_filters = []

                for title in unique_titles:
                    title_lower = title.lower()
                    # Filtros válidos basados en palabras clave comunes
                    if any(keyword in title_lower for keyword in [
                        'categoría', 'subcategoría', 'marca', 'precio', 'tipo', 'color',
                        'tamaño', 'capacidad', 'peso', 'voltaje', 'potencia', 'memoria',
                        'procesador', 'pantalla', 'batería', 'conectividad', 'sistema',
                        'eficiencia', 'consumo', 'origen', 'garantía'
                    ]) or len(title.split()) <= 4:
                        # Excluir elementos que parezcan ser opciones específicas
                        if not re.search(r'\d+(\s*(kg|l|ml|cm|w|hz|rpm|gb|tb|inch))', title_lower):
                            if not title.startswith(('Mostrar', 'Ver', 'Más')):
                                filter_section_titles.append(title)

                return filter_section_titles[:20]  # Limitar a 20 títulos más relevantes

            else:
                logger.warning(f"No se encontró contenedor de filtros para {category_name}")
                return []

        except Exception as e:
            logger.error(f"Error procesando {category_name}: {str(e)}")
            return []

    def scrape_all_categories(self):
        """Scrape todas las categorías y retorna los resultados"""
        results = {}

        for category_name, url in self.categories:
            logger.info(f"Iniciando scraping de {category_name}")
            filters = self.extract_filter_titles(url, category_name)
            results[category_name] = {
                'url': url,
                'filters': filters,
                'total_filters': len(filters)
            }

            # Pequeña pausa para no sobrecargar el servidor
            time.sleep(1)

        return results

    def generate_markdown_report(self, results):
        """Genera un reporte en formato Markdown"""
        markdown_content = "# Categorías de Jumbo\n\n## Lista de Categorías\n\n"

        for i, (name, url) in enumerate(self.categories, 1):
            markdown_content += f"{i}. {name}: {url}\n"

        markdown_content += "\n## Filtros por Categoría\n\n"

        for category_name, data in results.items():
            markdown_content += f"### {category_name}\n"
            markdown_content += f"**Total de filtros: {data['total_filters']}**\n"
            markdown_content += "-- FiltrosCategory\n"
            markdown_content += "Categoría\n"
            markdown_content += "Sub-Categoría\n"
            markdown_content += "-- Tipo de producto\n"
            markdown_content += "Tipo de Producto\n"
            markdown_content += "-- Subfiltros\n"

            # Filtrar y organizar los filtros
            filters = data['filters']
            # Remover 'Categoría', 'Sub-Categoría', 'Tipo de Producto' si están en la lista
            subfilters = [f for f in filters if f not in ['Categoría', 'Sub-Categoría', 'Tipo de Producto', 'Rangos de precio']]

            for filter_name in subfilters:
                markdown_content += f"{filter_name}\n"

            markdown_content += "\n"

        return markdown_content

    def save_results(self, results, output_dir="output"):
        """Guarda los resultados en archivos"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Guardar resultados JSON
        json_path = output_path / "filtros_jumbo.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # Guardar reporte Markdown
        markdown_content = self.generate_markdown_report(results)
        markdown_path = output_path / "categorias_jumbo.md"
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Resultados guardados en {output_path}")
        return json_path, markdown_path

def main():
    """Función principal"""
    scraper = JumboScraper()

    logger.info("Iniciando scraping de Jumbo...")
    results = scraper.scrape_all_categories()

    logger.info("Generando reportes...")
    json_path, markdown_path = scraper.save_results(results, "e:/scrapersTemp/scraperJumbo/output")

    logger.info("Scraping completado!")
    logger.info(f"Resultados JSON: {json_path}")
    logger.info(f"Reporte Markdown: {markdown_path}")

    # Mostrar resumen
    print("\n=== RESUMEN DEL SCRAPING ===")
    for category, data in results.items():
        print(f"{category}: {data['total_filters']} filtros encontrados")

if __name__ == "__main__":
    main()
