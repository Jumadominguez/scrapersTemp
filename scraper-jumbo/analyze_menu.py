#!/usr/bin/env python3
"""
Análisis del menú de categorías principal - Etapa 3.3
Filtrar y validar categorías extraídas
"""

import sys
from pathlib import Path
import json
import requests
import time
from urllib.parse import urljoin

# Agregar el directorio src al path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from scraper import JumboScraper

def filter_and_validate_categories(input_file='categories_extracted.json', output_file='categories_filtered.json'):
    """Filtrar y validar categorías - Etapa 3.3"""
    print('🚀 INICIANDO FILTRADO Y VALIDACIÓN DE CATEGORÍAS - ETAPA 3.3')
    print('=' * 60)

    # Cargar categorías extraídas
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            categories = json.load(f)
        print(f'📂 Cargadas {len(categories)} categorías del archivo {input_file}')
    except FileNotFoundError:
        print(f'❌ Error: No se encontró el archivo {input_file}')
        return []
    except json.JSONDecodeError as e:
        print(f'❌ Error al leer JSON: {e}')
        return []

    # Categorías a excluir (según especificación)
    categories_to_exclude = [
        'viví saludable', 'vivi saludable',  # Se considera no relevante
        'ofertas', 'novedades', 'promociones',  # Categorías promocionales
        'servicios', 'atención al cliente', 'contacto'  # No son categorías de productos
    ]

    filtered_categories = []
    validated_categories = []

    print('\n🔍 FILTRANDO CATEGORÍAS NO RELEVANTES...')
    print('-' * 40)

    for category in categories:
        name_lower = category['name'].lower().strip()

        # Verificar si debe excluirse
        should_exclude = False
        for exclude_term in categories_to_exclude:
            if exclude_term in name_lower:
                should_exclude = True
                print(f'🚫 Excluyendo: "{category["name"]}" (contiene "{exclude_term}")')
                break

        if not should_exclude:
            filtered_categories.append(category)
            print(f'✅ Manteniendo: "{category["name"]}"')

    print(f'\n📊 Después del filtrado: {len(filtered_categories)} categorías')

    # Validar URLs
    print('\n🔗 VALIDANDO URLs DE CATEGORÍAS...')
    print('-' * 40)

    scraper = JumboScraper()
    base_url = 'https://www.jumbo.com.ar/'

    for i, category in enumerate(filtered_categories, 1):
        url = category['url']
        name = category['name']

        print(f'{i:2d}. Validando: {name}')
        print(f'    URL: {url}')

        try:
            # Hacer petición HEAD para validar URL (más rápido que GET completo)
            response = requests.head(url, timeout=10, allow_redirects=True,
                                   headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

            if response.status_code == 200:
                print(f'    ✅ URL válida (Status: {response.status_code})')
                validated_categories.append(category)
            else:
                print(f'    ⚠️  URL no válida (Status: {response.status_code})')

        except requests.RequestException as e:
            print(f'    ❌ Error de conexión: {str(e)[:50]}...')

        # Pequeña pausa para no sobrecargar el servidor
        time.sleep(0.5)

    print(f'\n📊 Después de validación: {len(validated_categories)} categorías válidas')

    # Limpiar nombres de categorías
    print('\n🧹 LIMPIANDO NOMBRES DE CATEGORÍAS...')
    print('-' * 40)

    for category in validated_categories:
        original_name = category['name']
        # Limpiar nombre (remover espacios extra, caracteres especiales)
        clean_name = ' '.join(original_name.split())  # Normalizar espacios
        clean_name = clean_name.title()  # Capitalizar correctamente

        category['name'] = clean_name
        category['name_cleaned'] = clean_name != original_name

        if clean_name != original_name:
            print(f'🧽 "{original_name}" → "{clean_name}"')
        else:
            print(f'✅ "{clean_name}" (sin cambios)')

    # Guardar categorías filtradas y validadas
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validated_categories, f, indent=2, ensure_ascii=False)

    print(f'\n💾 CATEGORÍAS GUARDADAS EN: {output_file}')

    # Mostrar resumen final
    print('\n📊 RESUMEN FINAL - ETAPA 3.3')
    print('=' * 40)
    print(f'📂 Categorías iniciales: {len(categories)}')
    print(f'🔍 Después del filtrado: {len(filtered_categories)}')
    print(f'🔗 Después de validación: {len(validated_categories)}')
    print(f'💾 Archivo generado: {output_file}')

    if validated_categories:
        print('\n📋 LISTADO DE CATEGORÍAS VALIDADAS:')
        print('-' * 40)
        for i, category in enumerate(validated_categories, 1):
            print(f'{i:2d}. {category["name"]}')

    return validated_categories

if __name__ == "__main__":
    filter_and_validate_categories()

def extract_categories_from_menu(driver):
    """Extraer todas las categorías del menú desplegado"""
    categories = []

    try:
        # Esperar a que el menú se despliegue completamente
        time.sleep(3)

        # Buscar específicamente dentro del menú desplegado VTEX
        # Primero intentar encontrar el contenedor del menú desplegado
        menu_container_selectors = [
            '.vtex-menu-2-x-menuContainer',  # Contenedor principal del menú
            '.vtex-menu-2-x-submenu',       # Submenú desplegado
            '[class*="menuContainer"]',     # Contenedor genérico
            '.vtex-menu-2-x-menuItem',      # Items del menú
        ]

        menu_container = None
        for selector in menu_container_selectors:
            try:
                containers = driver.find_elements(By.CSS_SELECTOR, selector)
                for container in containers:
                    # Verificar si el contenedor es visible y tiene contenido
                    if container.is_displayed() and container.size['height'] > 50:
                        menu_container = container
                        print(f'✅ Contenedor del menú encontrado: {selector}')
                        break
                if menu_container:
                    break
            except:
                continue

        if not menu_container:
            print('⚠️  No se encontró contenedor específico del menú, usando página completa')

        # Selectores más específicos para categorías del menú desplegado
        category_selectors = [
            '.vtex-menu-2-x-menuItem a[href*="/"]',           # Enlaces en items del menú VTEX
            '.vtex-menu-2-x-submenuItem a[href*="/"]',       # Items del submenú
            '.vtex-menu-2-x-styledLink[href*="/"]',          # Enlaces estilizados del menú
        ]

        found_links = set()  # Evitar duplicados

        for selector in category_selectors:
            try:
                if menu_container:
                    # Buscar dentro del contenedor del menú
                    elements = menu_container.find_elements(By.CSS_SELECTOR, selector.replace('.vtex-menu-2-x-menuItem ', ''))
                else:
                    # Buscar en toda la página
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)

                print(f'🔍 Selector {selector}: {len(elements)} elementos encontrados')

                for element in elements:
                    try:
                        href = element.get_attribute('href')
                        text = element.text.strip()

                        if href and text and len(text) > 1 and len(text) < 50:
                            # Filtrar URLs válidas de categorías principales
                            if (href.startswith('https://www.jumbo.com.ar/') and
                                not href.endswith('/p') and  # No productos individuales
                                not 'javascript:' in href and
                                not '#' in href and
                                not '/p/' in href and       # No páginas de producto
                                not 'descuentos' in href.lower() and  # No descuentos
                                not 'sucursales' in href.lower() and  # No sucursales
                                not 'arrepentimiento' in href.lower() and  # No botón arrepentimiento
                                not 'legales' in text.lower() and     # No legales
                                not 'bancarios' in text.lower()):     # No bancarios

                                # Limpiar el texto (remover caracteres extraños)
                                clean_text = re.sub(r'[^\w\sáéíóúñÁÉÍÓÚÑ]', '', text).strip()

                                if clean_text and len(clean_text) > 2:
                                    # Verificar que no sea un enlace genérico
                                    generic_terms = [
                                        'ver más', 'ver todo', 'todos', 'ofertas', 'novedades',
                                        'comprar', 'compra', 'inicio', 'home', 'contacto',
                                        'ayuda', 'servicio', 'atención', 'sucursales',
                                        'legales', 'bancarios', 'arrepentimiento'
                                    ]

                                    is_generic = False
                                    for term in generic_terms:
                                        if term in clean_text.lower():
                                            is_generic = True
                                            break

                                    if not is_generic:
                                        category_entry = {
                                            'name': clean_text,
                                            'url': href,
                                            'text_original': text
                                        }

                                        # Usar URL como clave para evitar duplicados
                                        if href not in found_links:
                                            found_links.add(href)
                                            categories.append(category_entry)
                                            print(f'✅ Categoría encontrada: {clean_text}')

                    except Exception as e:
                        print(f'⚠️  Error procesando elemento: {e}')
                        continue

            except Exception as e:
                print(f'⚠️  Selector {selector} falló: {e}')
                continue

        # Filtrar categorías principales (última validación)
        main_categories = []
        exclude_keywords = [
            'ver más', 'ver todo', 'todos', 'ofertas', 'novedades',
            'comprar', 'compra', 'inicio', 'home', 'contacto',
            'ayuda', 'servicio', 'atención', 'sucursales', 'legales',
            'bancarios', 'arrepentimiento', 'descuentos'
        ]

        for category in categories:
            name_lower = category['name'].lower()
            should_exclude = False

            for keyword in exclude_keywords:
                if keyword in name_lower:
                    should_exclude = True
                    break

            if not should_exclude and len(category['name']) > 2:
                main_categories.append(category)

        print(f'📊 Categorías válidas después del filtrado: {len(main_categories)}')
        return main_categories

    except Exception as e:
        print(f'❌ Error extrayendo categorías: {e}')
        return []

def analyze_main_menu():
    """Extraer categorías principales del menú desplegado - Etapa 3.2"""
    scraper = JumboScraper()
    url = 'https://www.jumbo.com.ar/'

    print('🚀 INICIANDO EXTRACCIÓN DE CATEGORÍAS - ETAPA 3.2')
    print('=' * 50)

    # Configurar Selenium con Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Abrir en pantalla completa
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print('✅ NAVEGADOR SELENIUM INICIADO')
    except Exception as e:
        print(f'❌ Error iniciando Selenium: {e}')
        print('Asegúrate de tener ChromeDriver instalado')
        return

    try:
        print('📡 CARGANDO PÁGINA EN SELENIUM...')
        driver.get(url)
        time.sleep(3)  # Esperar a que cargue la página

        print('🔍 BUSCANDO ELEMENTO DEL MENÚ DESPLEGABLE...')

        # Buscar el elemento span con las clases específicas
        try:
            menu_trigger = driver.find_element(By.CSS_SELECTOR, 'span.vtex-menu-2-x-styledLink--header-category')
            print('✅ ELEMENTO TRIGGER DEL MENÚ ENCONTRADO')
            print(f'Texto del elemento: "{menu_trigger.text}"')

            if menu_trigger.text.upper() == 'CATEGORÍAS':
                print('🎯 ELEMENTO CORRECTO IDENTIFICADO: "CATEGORÍAS"')
            else:
                print(f'⚠️  Texto encontrado: "{menu_trigger.text}" (esperaba "CATEGORÍAS")')

        except Exception as e:
            print(f'❌ Error encontrando el elemento: {e}')
            print('Buscando alternativa con XPath...')

            try:
                # Buscar por XPath como alternativa
                menu_trigger = driver.find_element(By.XPATH, "//span[contains(@class, 'vtex-menu-2-x-styledLink--header-category')]")
                print('✅ ELEMENTO ENCONTRADO CON XPATH')
                print(f'Texto del elemento: "{menu_trigger.text}"')
            except Exception as e2:
                print(f'❌ Error con XPath también: {e2}')
                return

        print('\n🖱️  HACIENDO HOVER SOBRE EL ELEMENTO...')
        print('=' * 50)

        # Crear ActionChains para hacer hover
        actions = ActionChains(driver)

        # Mover el mouse al elemento (hover)
        actions.move_to_element(menu_trigger).perform()

        print('✅ HOVER REALIZADO')
        print('📋 MENÚ DE CATEGORÍAS DESPLEGADO')

        # Extraer categorías del menú desplegado
        print('\n🔍 EXTRAYENDO CATEGORÍAS DEL MENÚ DESPLEGADO...')
        print('=' * 50)

        categories = extract_categories_from_menu(driver)

        print(f'📊 CATEGORÍAS EXTRAÍDAS: {len(categories)}')

        if categories:
            print('\n📋 LISTADO DE CATEGORÍAS ENCONTRADAS:')
            print('=' * 50)

            for i, category in enumerate(categories, 1):
                print(f'{i:2d}. {category["name"]}')
                print(f'    URL: {category["url"]}')

            # Guardar categorías en archivo JSON
            output_file = 'categories_extracted.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(categories, f, indent=2, ensure_ascii=False)

            print(f'\n💾 CATEGORÍAS GUARDADAS EN: {output_file}')

            # Mostrar resumen
            print(f'\n📊 RESUMEN DE EXTRACCIÓN:')
            print(f'   - Total de categorías: {len(categories)}')
            print(f'   - Archivo generado: {output_file}')

        else:
            print('❌ No se encontraron categorías en el menú desplegado')

        # Mantener la página abierta para verificación
        print('\n⏳ MANTENIENDO PÁGINA ABIERTA PARA VERIFICACIÓN...')
        print('👀 Verifica las categorías extraídas y el menú desplegado')
        print('Presiona Ctrl+C cuando hayas terminado de verificar')

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('\n✅ VERIFICACIÓN COMPLETADA POR EL USUARIO')

    except Exception as e:
        print(f'❌ Error durante la ejecución: {e}')
    finally:
        print('\n🔄 CERRANDO NAVEGADOR...')
        try:
            driver.quit()
        except:
            pass

    print('\n✅ TAREA 3.2 COMPLETADA')
    print('🖱️  HOVER REALIZADO Y CATEGORÍAS EXTRAÍDAS')
    print(f'� TOTAL DE CATEGORÍAS: {len(categories) if "categories" in locals() else 0}')

if __name__ == "__main__":
    filter_and_validate_categories()
