from bs4 import BeautifulSoup
import re

def simple_filter_search():
    """Búsqueda simple de filtros en el HTML"""

    with open('Sandbox/almacen_full_source.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    print("=== BÚSQUEDA SIMPLE DE FILTROS ===\n")

    # Buscar todas las menciones de filtros comunes
    filter_patterns = [
        'Categoría', 'Marca', 'Tipo de Producto', 'Contenido', 'Envase',
        'Sabor', 'Elaboración', 'Origen', 'Formato', 'Variedad',
        'Cantidad', 'Presentación', 'Sub-Categoría'
    ]

    found_filters = set()

    for pattern in filter_patterns:
        # Buscar en todo el texto del documento
        elements = soup.find_all(text=re.compile(re.escape(pattern)))
        if elements:
            found_filters.add(pattern)
            print(f"✅ {pattern}: encontrado en {len(elements)} lugares")

    print(f"\n📊 Total de filtros encontrados: {len(found_filters)}")
    print("Filtros encontrados:", sorted(found_filters))

    # Buscar elementos con clase filter
    filter_elements = soup.find_all(class_=re.compile('.*filter.*'))
    print(f"\n🔍 Elementos con clase 'filter': {len(filter_elements)}")

    for elem in filter_elements[:10]:  # Mostrar solo los primeros 10
        text = elem.get_text(strip=True)
        if text and len(text) > 1:
            print(f"  - {text}")

if __name__ == "__main__":
    simple_filter_search()
