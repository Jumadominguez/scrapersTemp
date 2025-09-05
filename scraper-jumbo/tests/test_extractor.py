#!/usr/bin/env python3
"""
Tests para la función extract_categories
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock

# Agregar el directorio src al path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from extractor import extract_categories


class TestExtractCategories:
    """Tests para la función extract_categories"""

    def test_extract_categories_with_valid_html(self):
        """Test con HTML que contiene categorías válidas"""
        html_content = '''
        <html>
        <body>
            <a href="/almacen">Almacén</a>
            <a href="/bebidas">Bebidas</a>
            <a href="/lacteos">Lácteos</a>
            <a href="/login">Iniciar Sesión</a>
            <a href="/carrito">Carrito</a>
            <a href="https://external.com">Enlace Externo</a>
        </body>
        </html>
        '''

        categories = extract_categories(html_content)

        # Debería encontrar 3 categorías válidas
        assert len(categories) == 3

        # Verificar que las categorías sean correctas
        category_names = [cat['name'] for cat in categories]
        assert 'Almacén' in category_names
        assert 'Bebidas' in category_names
        assert 'Lácteos' in category_names

        # Verificar URLs
        category_urls = [cat['url'] for cat in categories]
        assert 'https://www.jumbo.com.ar/almacen' in category_urls
        assert 'https://www.jumbo.com.ar/bebidas' in category_urls
        assert 'https://www.jumbo.com.ar/lacteos' in category_urls

    def test_extract_categories_filters_invalid_links(self):
        """Test que filtra correctamente enlaces no válidos"""
        html_content = '''
        <html>
        <body>
            <a href="/almacen">Almacén</a>
            <a href="/login">Iniciar Sesión</a>
            <a href="/carrito">Carrito</a>
            <a href="/ofertas">Ofertas</a>
            <a href="javascript:void(0)">JavaScript</a>
            <a href="#top">Anchor</a>
            <a href="https://external.com">Externo</a>
            <a href="/ayuda">Ayuda</a>
            <a href="/contacto">Contacto</a>
        </body>
        </html>
        '''

        categories = extract_categories(html_content)

        # Solo debería encontrar Almacén
        assert len(categories) == 1
        assert categories[0]['name'] == 'Almacén'
        assert categories[0]['url'] == 'https://www.jumbo.com.ar/almacen'

    def test_extract_categories_with_empty_html(self):
        """Test con HTML vacío"""
        categories = extract_categories("")
        assert categories == []

    def test_extract_categories_with_no_links(self):
        """Test con HTML sin enlaces"""
        html_content = '<html><body><h1>Sin enlaces</h1></body></html>'
        categories = extract_categories(html_content)
        assert categories == []

    def test_extract_categories_avoids_duplicates(self):
        """Test que evita duplicados por URL"""
        html_content = '''
        <html>
        <body>
            <a href="/almacen">Almacén</a>
            <a href="/almacen">Almacén Duplicado</a>
            <div><a href="/bebidas">Bebidas</a></div>
        </body>
        </html>
        '''

        categories = extract_categories(html_content)

        # Debería tener solo 2 categorías (sin duplicados)
        assert len(categories) == 2
        category_names = [cat['name'] for cat in categories]
        assert 'Almacén' in category_names
        assert 'Bebidas' in category_names

    def test_extract_categories_with_menu_elements(self):
        """Test con elementos de menú específicos"""
        html_content = '''
        <html>
        <body>
            <nav class="menu-principal">
                <a href="/almacen">Almacén</a>
                <a href="/bebidas">Bebidas</a>
            </nav>
            <div class="navigation">
                <a href="/lacteos">Lácteos</a>
            </div>
        </body>
        </html>
        '''

        categories = extract_categories(html_content)

        # Debería encontrar las 3 categorías
        assert len(categories) >= 3
        category_names = [cat['name'] for cat in categories]
        assert 'Almacén' in category_names
        assert 'Bebidas' in category_names
        assert 'Lácteos' in category_names

    def test_extract_categories_filters_long_text(self):
        """Test que filtra textos muy largos (productos)"""
        html_content = '''
        <html>
        <body>
            <a href="/almacen">Almacén</a>
            <a href="/producto-123">Producto muy largo con descripción completa que debería ser filtrado porque es un producto individual y no una categoría</a>
        </body>
        </html>
        '''

        categories = extract_categories(html_content)

        # Solo debería encontrar Almacén
        assert len(categories) == 1
        assert categories[0]['name'] == 'Almacén'
