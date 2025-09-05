"""
Módulo Extractor - Extracción de categorías y filtros
"""

import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from config import get_logger


logger = get_logger()


def extract_categories(html_content: str) -> List[Dict[str, Any]]:
    """
    Extrae las categorías principales de la página de Jumbo

    Args:
        html_content (str): Contenido HTML de la página principal

    Returns:
        List[Dict[str, Any]]: Lista de categorías con nombre y URL
    """
    logger.info("📂 Extrayendo categorías de la página principal...")

    if not html_content:
        logger.warning("⚠️ Contenido HTML vacío")
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    categories = []

    # Estrategia 1: Buscar todos los enlaces que podrían ser categorías
    all_links = soup.find_all('a', href=re.compile(r'^/[a-z-]+'))

    for link in all_links:
        href = link.get('href')
        text = link.get_text().strip()

        # Filtros para identificar categorías válidas
        if (href and
            len(href) > 3 and
            not href.startswith(('http', 'javascript:', '#', 'mailto:')) and
            len(text) > 2 and
            len(text) < 50 and  # Evitar textos muy largos (productos)
            not any(word in href.lower() for word in ['login', 'carrito', 'ofertas', 'novedades', 'ayuda', 'contacto', 'sucursales', 'entrega', 'actualiza', 'descuentos']) and
            not any(word in text.lower() for word in ['ver', 'click', 'comprar', 'precio', 'regular', 'producto', 'descuentos', 'sucursal', 'entrega', 'actualiza'])):

            full_url = f"https://www.jumbo.com.ar{href}"

            # Evitar duplicados por URL
            if not any(cat['url'] == full_url for cat in categories):
                categories.append({
                    'name': text,
                    'url': full_url,
                    'filters': []
                })

    # Estrategia 2: Buscar en elementos específicos de menú
    menu_selectors = [
        ('[class*="menu"]', 'Elementos de menú'),
        ('[class*="nav"]', 'Elementos de navegación'),
        ('[class*="category"]', 'Elementos de categoría'),
        ('nav', 'Etiquetas nav'),
        ('[role="navigation"]', 'Role navigation')
    ]

    for selector, description in menu_selectors:
        try:
            menu_elements = soup.select(selector)
            for menu_elem in menu_elements:
                links = menu_elem.find_all('a', href=re.compile(r'^/[a-z-]+'))
                for link in links:
                    href = link.get('href')
                    text = link.get_text().strip()

                    if (href and len(text) > 2 and len(text) < 50 and
                        not any(word in href.lower() for word in ['login', 'carrito', 'ofertas', 'novedades', 'ayuda', 'contacto', 'sucursales', 'entrega'])):

                        full_url = f"https://www.jumbo.com.ar{href}"

                        # Evitar duplicados
                        if not any(cat['url'] == full_url for cat in categories):
                            categories.append({
                                'name': text,
                                'url': full_url,
                                'filters': []
                            })
        except Exception as e:
            logger.debug(f"Error buscando {description}: {e}")

    logger.info(f"� Encontradas {len(categories)} categorías potenciales")
    return categories


def extract_filters_from_category(scraper, category_url: str) -> List[str]:
    """
    Extrae los filtros de una categoría específica

    Args:
        scraper: Instancia del JumboScraper
        category_url (str): URL de la categoría

    Returns:
        List[str]: Lista de nombres de filtros
    """
    logger.info(f"🔍 Extrayendo filtros de: {category_url}")

    # Obtener contenido de la página de categoría
    html_content = scraper.get_page(category_url)

    if not html_content:
        logger.warning(f"⚠️ No se pudo obtener contenido de {category_url}")
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    filters = []

    # Filtros base que siempre deben estar presentes
    base_filters = ['Categoría', 'Sub-Categoría', 'Tipo de Producto']

    # Buscar elementos que contengan filtros
    # Jumbo puede usar diferentes selectores

    # Método 1: Buscar por texto que contenga "Mostrar"
    show_more_elements = soup.find_all(string=re.compile(r'Mostrar \d+ más'))
    for element in show_more_elements:
        # El filtro suele estar antes de "Mostrar X más"
        parent = element.parent if element.parent else element
        filter_text = parent.get_text().strip()

        # Extraer el nombre del filtro (antes de "Mostrar")
        if 'Mostrar' in filter_text:
            filter_name = filter_text.split('Mostrar')[0].strip()
            if (len(filter_name) > 1 and
                filter_name not in base_filters and
                'precio' not in filter_name.lower()):
                filters.append(filter_name)

    # Método 2: Buscar elementos con clases relacionadas a filtros
    filter_classes = [
        'filter-item', 'facet', 'filter-option',
        'search-filter', 'filter-group'
    ]

    for class_name in filter_classes:
        filter_elements = soup.find_all(class_=re.compile(class_name))
        for element in filter_elements:
            text = element.get_text().strip()
            if (len(text) > 2 and
                text not in base_filters and
                'precio' not in text.lower() and
                text not in filters):
                filters.append(text)

    # Método 3: Buscar en scripts embebidos (JSON con filtros)
    scripts = soup.find_all('script', string=re.compile(r'filter|facet'))
    for script in scripts:
        if script.string:
            # Buscar patrones de filtros en JavaScript
            filter_patterns = [
                r'"name"\s*:\s*"([^"]+)"',
                r'filters.*?"([^"]+)"',
                r'facets.*?"([^"]+)"'
            ]

            for pattern in filter_patterns:
                matches = re.findall(pattern, script.string, re.IGNORECASE)
                for match in matches:
                    if (len(match) > 2 and
                        match not in base_filters and
                        'precio' not in match.lower() and
                        match not in filters):
                        filters.append(match)

    # Limpiar y validar filtros
    cleaned_filters = []
    for f in filters:
        # Remover caracteres especiales y espacios extra
        cleaned = re.sub(r'[^\w\s\-áéíóúñ]', '', f).strip()
        if (len(cleaned) >= 2 and
            len(cleaned) <= 50 and  # Máximo razonable
            cleaned not in base_filters):
            cleaned_filters.append(cleaned)

    # Remover duplicados y ordenar
    unique_filters = list(set(cleaned_filters))
    unique_filters.sort()

    all_filters = base_filters + unique_filters

    logger.info(f"✅ Extraídos {len(unique_filters)} filtros específicos de {category_url}")
    return all_filters


def validate_category_url(url: str) -> bool:
    """
    Valida que una URL sea de una categoría válida de Jumbo

    Args:
        url (str): URL a validar

    Returns:
        bool: True si es válida
    """
    if not url or not url.startswith('https://www.jumbo.com.ar'):
        return False

    # Evitar URLs de páginas que no son categorías
    invalid_patterns = [
        '/login', '/carrito', '/checkout', '/ofertas',
        '/novedades', '/mi-cuenta', '/contacto'
    ]

    return not any(pattern in url for pattern in invalid_patterns)


def clean_filter_name(filter_name: str) -> str:
    """
    Limpia y normaliza un nombre de filtro

    Args:
        filter_name (str): Nombre del filtro a limpiar

    Returns:
        str: Nombre del filtro limpio
    """
    if not filter_name:
        return ""

    # Remover caracteres especiales pero mantener letras, números, espacios y guiones
    cleaned = re.sub(r'[^\w\s\-áéíóúñÁÉÍÓÚÑ]', '', filter_name)

    # Normalizar espacios
    cleaned = ' '.join(cleaned.split())

    return cleaned.strip()
