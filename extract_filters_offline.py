from bs4 import BeautifulSoup
import os

def extract_filters_from_html(file_path, name):
    """Extraer filtros de un archivo HTML guardado"""
    filters = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Buscar elementos de filtro en el sidebar/accordion
        filter_sidebar = soup.find('div', class_='vtex-search-result-3-x-accordionFilter')
        if filter_sidebar:
            print(f"{name}: Found filter sidebar")

            # Buscar todos los items de filtro
            filter_items = filter_sidebar.find_all('div', class_='vtex-search-result-3-x-accordionFilterItemTitle')
            print(f"{name}: Found {len(filter_items)} filter items")

            for i, item in enumerate(filter_items):
                title = item.get_text(strip=True)
                print(f"{name}: Item {i} text: '{title}' (length: {len(title)})")

                if title and not any(word in title.lower() for word in ['precio', 'regular', 'impuestos', 'nacionales', '$', 'kg', 'lt', 'gr']):
                    filters.append(f"Filter: {title}")
                    print(f"{name}: Extracted filter: {title}")

        # Método alternativo: buscar por texto específico
        filter_keywords = ["Categoría", "Marca", "Tipo de Producto", "Contenido", "Envase", "Sub-Categoría", "Elaboración", "Sabor"]

        for keyword in filter_keywords:
            elements = soup.find_all(text=lambda text: text and keyword in text)
            if elements:
                print(f"{name}: Found keyword '{keyword}' in {len(elements)} text elements")
                for elem in elements:
                    text = elem.strip()
                    if text == keyword:
                        filters.append(f"Filter: {keyword}")
                        break

        print(f"{name}: Total filters found: {len(filters)}")
        return filters

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

# Procesar archivos HTML guardados
lacteos_filters = extract_filters_from_html('Sandbox/lacteos_full_source.html', 'Lácteos')
almacen_filters = extract_filters_from_html('Sandbox/almacen_full_source.html', 'Almacén')

# Escribir comparación
with open('Sandbox/comparacion_filtros_sin_precio.md', 'w', encoding='utf-8') as f:
    f.write("# Comparación de Filtros (sin precios): Lácteos vs Almacén\n\n")
    f.write("## Filtros en Lácteos\n")
    for fl in lacteos_filters:
        f.write(f"- {fl}\n")
    f.write("\n## Filtros en Almacén\n")
    for fl in almacen_filters:
        f.write(f"- {fl}\n")
    f.write("\n## Diferencias\n")
    if lacteos_filters and not almacen_filters:
        f.write("En Lácteos se encontraron filtros, en Almacén no.\n")
    elif almacen_filters and not lacteos_filters:
        f.write("En Almacén se encontraron filtros, en Lácteos no.\n")
    else:
        f.write("Ambas categorías tienen filtros similares.\n")

print("Comparación completada. Revisa Sandbox/comparacion_filtros_sin_precio.md")
