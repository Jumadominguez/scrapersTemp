#!/usr/bin/env python3
"""
Análisis del menú de categorías principal - Etapa 2 Paso 2
Buscar menú desplegable de categorías
"""

import sys
from pathlib import Path
import webbrowser
import time

# Agregar el directorio src al path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from scraper import JumboScraper
from bs4 import BeautifulSoup
import re

def open_in_browser(url, delay=2):
    """Abre una URL en el navegador con un delay"""
    print(f"🌐 Abriendo en navegador: {url}")
    webbrowser.open(url)
    time.sleep(delay)

def analyze_main_menu():
    """Buscar el menú desplegable de categorías - Etapa 2 Paso 2"""
    scraper = JumboScraper()
    url = 'https://www.jumbo.com.ar/'

    print('🚀 INICIANDO ANÁLISIS DEL MENÚ - ETAPA 2 PASO 2')
    print('=' * 50)

    # Abrir la página principal en el navegador
    open_in_browser(url, 3)

    print('📡 OBTENIENDO CONTENIDO DE LA PÁGINA...')
    html = scraper.get_page(url)

    if not html:
        print("❌ Error obteniendo la página")
        return

    soup = BeautifulSoup(html, 'html.parser')

    print('🔍 BUSCANDO ELEMENTO DEL MENÚ DESPLEGABLE...')
    print('=' * 50)

    # Buscar el elemento específico del menú desplegable
    # Primero buscar el nav container
    nav_menu = soup.find('nav', class_=re.compile(r'vtex-menu-2-x-menuContainerNav.*category-menu'))

    if nav_menu:
        print('✅ CONTENEDOR NAV DEL MENÚ ENCONTRADO')

        # Buscar el span que contiene el texto "CATEGORÍAS"
        menu_trigger = nav_menu.find('span', class_=re.compile(r'vtex-menu-2-x-styledLink.*header-category'))

        if menu_trigger:
            print('✅ ELEMENTO TRIGGER DEL MENÚ ENCONTRADO')
            print(f'Tag: {menu_trigger.name}')
            print(f'Clases: {menu_trigger.get("class")}')
            print(f'Texto: {menu_trigger.get_text(strip=True)}')
        else:
            print('❌ No se encontró el span trigger dentro del nav')
            return
    else:
        print('❌ No se encontró el contenedor nav del menú')
        print('Buscando alternativas...')

        # Buscar por el div con "CATEGORÍAS"
        menu_trigger = soup.find('div', class_=re.compile(r'vtex-menu-2-x-styledLinkContent.*header-category'))

        if not menu_trigger:
            print('❌ No se encontró el elemento del menú desplegable')
            return

        print('✅ ELEMENTO DEL MENÚ ENCONTRADO (alternativo)')
        print(f'Tag: {menu_trigger.name}')
        print(f'Clases: {menu_trigger.get("class")}')
        print(f'Texto: {menu_trigger.get_text(strip=True)}')

    print('\n🔍 ANALIZANDO ESTRUCTURA DEL MENÚ...')
    print('=' * 50)

    # El menú desplegable se activa con hover, pero en HTML estático
    # necesitamos buscar elementos que contengan las categorías
    # Vamos a buscar en toda la página elementos que parezcan menús de categorías

    # Buscar todos los divs que podrían contener categorías
    all_divs = soup.find_all('div')
    menu_candidates = []

    for div in all_divs:
        links = div.find_all('a', href=re.compile(r'^/'))
        if len(links) >= 10:  # Buscar contenedores con al menos 10 enlaces
            category_count = 0
            for link in links:
                text = link.get_text(strip=True)
                if text and len(text) > 2:
                    # Contar enlaces que parecen categorías principales
                    if any(keyword in text.lower() for keyword in [
                        'almacén', 'bebidas', 'carnes', 'lácteos', 'limpieza', 'perfumería',
                        'electro', 'hogar', 'jardín', 'mascotas', 'bebés', 'niños',
                        'deportes', 'belleza', 'salud', 'panadería', 'congelados',
                        'frutas', 'verduras', 'pescados', 'mariscos', 'quesos', 'fiambres'
                    ]):
                        category_count += 1

            if category_count >= 8:  # Si tiene al menos 8 categorías principales
                menu_candidates.append((div, len(links), category_count))

    if menu_candidates:
        # Ordenar por número de categorías (de mayor a menor)
        menu_candidates.sort(key=lambda x: x[2], reverse=True)
        dropdown_menu = menu_candidates[0][0]

        print(f'🎯 MENÚ DESPLEGABLE IDENTIFICADO: {dropdown_menu.name}')
        print(f'   - Enlaces totales: {menu_candidates[0][1]}')
        print(f'   - Categorías identificadas: {menu_candidates[0][2]}')

        # Mostrar algunas clases del elemento encontrado para debugging
        classes = dropdown_menu.get('class')
        if classes:
            print(f'   - Clases: {classes[:3]}...')  # Mostrar primeras 3 clases

    else:
        print('❌ No se encontraron contenedores con suficientes categorías')
        print('El menú desplegable podría cargarse dinámicamente con JavaScript')
        return

    print('\n📋 EXTRAYENDO CATEGORÍAS DEL MENÚ')
    print('=' * 50)

    # Extraer todas las categorías del menú encontrado
    menu_links = dropdown_menu.find_all('a', href=True)
    categories_found = []

    print(f'Enlaces encontrados en el menú: {len(menu_links)}')

    for link in menu_links:
        text = link.get_text(strip=True)
        href = link.get('href')

        if text and href and len(text) > 1 and href.startswith('/'):
            # Filtrar enlaces no deseados
            exclude_keywords = [
                'ver producto', 'precio regular', 'actualizá tu navegador',
                'ver legales', 'descuentos bancarios', 'ofertas y catálogos',
                'compra rápida', 'encontrá tu sucursal', 'métodos de entrega'
            ]

            should_exclude = False
            for keyword in exclude_keywords:
                if keyword.lower() in text.lower():
                    should_exclude = True
                    break

            if not should_exclude:
                categories_found.append((text, href))
                print(f'  📍 {text} -> {href}')

    print(f'\n📊 CATEGORÍAS EXTRAÍDAS: {len(categories_found)}')

    # Mostrar resumen de categorías encontradas
    if categories_found:
        print('\n📋 RESUMEN DE CATEGORÍAS PRINCIPALES:')
        for i, (text, href) in enumerate(categories_found[:15], 1):  # Mostrar primeras 15
            print(f'  {i:2d}. {text}')

        if len(categories_found) > 15:
            print(f'  ... y {len(categories_found) - 15} categorías más')

    print('\n✅ ANÁLISIS COMPLETADO - ETAPA 2 PASO 2')
    print(f'📊 Total de categorías encontradas: {len(categories_found)}')
    print('🌐 PÁGINA HOME ABIERTA EN NAVEGADOR')
    print('📋 MENÚ DE CATEGORÍAS ANALIZADO Y EXTRAÍDO')

if __name__ == "__main__":
    analyze_main_menu()
