from bs4 import BeautifulSoup
import re

def verify_real_filters():
    """Verificar qué filtros están realmente presentes en el HTML"""

    with open('Sandbox/almacen_full_source.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    print("=== VERIFICACIÓN DE FILTROS REALES EN ALMACÉN ===\n")

    # Buscar específicamente en el sidebar de filtros
    filter_sidebar = soup.find('div', class_=re.compile('.*accordionFilter.*'))

    if filter_sidebar:
        print("✅ Encontrado sidebar de filtros")

        # Obtener todo el texto del sidebar
        sidebar_text = filter_sidebar.get_text()
        print(f"Texto completo del sidebar (primeros 500 caracteres):\n{sidebar_text[:500]}...\n")

        # Buscar menciones específicas de filtros
        filter_candidates = [
            'Categoría', 'Marca', 'Tipo de Producto', 'Contenido', 'Envase',
            'Sabor', 'Elaboración', 'Origen', 'Formato', 'Variedad',
            'Cantidad', 'Presentación', 'Sub-Categoría'
        ]

        print("🔍 Verificación de cada filtro candidato:")
        confirmed_filters = []

        for candidate in filter_candidates:
            if candidate in sidebar_text:
                print(f"  ✅ {candidate}: CONFIRMADO en sidebar")
                confirmed_filters.append(candidate)
            else:
                print(f"  ❌ {candidate}: NO encontrado en sidebar")

        print(f"\n📊 Filtros confirmados en sidebar: {len(confirmed_filters)}")
        print("Lista:", confirmed_filters)

    else:
        print("❌ No se encontró sidebar de filtros")

    # Buscar en todo el documento como backup
    print("\n=== BÚSQUEDA EN TODO EL DOCUMENTO ===")

    all_text = soup.get_text()
    print("Búsqueda general de términos de filtro:")
    for term in ['Presentación', 'Origen', 'Formato', 'Variedad']:
        count = all_text.count(term)
        print(f"  '{term}': aparece {count} veces")

if __name__ == "__main__":
    verify_real_filters()
