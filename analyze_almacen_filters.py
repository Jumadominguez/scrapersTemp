from bs4 import BeautifulSoup
import re

def analyze_almacen_filters():
    """Analizar en detalle los filtros disponibles en Almacén"""

    with open('Sandbox/almacen_full_source.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    print("=== ANÁLISIS DETALLADO DE FILTROS EN ALMACÉN ===\n")

    # Buscar el sidebar de filtros
    filter_sidebar = soup.find('div', class_=re.compile('.*accordionFilter.*'))
    if filter_sidebar:
        print("✅ Encontrado sidebar de filtros")
        print(f"Clases del sidebar: {filter_sidebar.get('class')}")

        # Buscar todos los títulos de filtro
        filter_titles = filter_sidebar.find_all(['div', 'span', 'h3', 'h4'], class_=re.compile('.*title.*|.*filter.*|.*accordion.*'))
        print(f"\n📋 Títulos de filtro encontrados ({len(filter_titles)}):")
        for i, title in enumerate(filter_titles):
            text = title.get_text(strip=True)
            if text and len(text) > 1:
                print(f"  {i+1}. {text}")

        # Buscar elementos que contengan texto de filtro
        all_text_elements = filter_sidebar.find_all(text=True)
        filter_keywords = []
        for text in all_text_elements:
            text_clean = text.strip()
            if text_clean and len(text_clean) > 1 and not any(word in text_clean.lower() for word in ['precio', 'ver', 'todos', 'filtrar', 'limpiar']):
                if text_clean not in filter_keywords:
                    filter_keywords.append(text_clean)

        print(f"\n🔍 Todos los textos encontrados en filtros ({len(filter_keywords)}):")
        for i, keyword in enumerate(filter_keywords):
            print(f"  {i+1}. {keyword}")

    else:
        print("❌ No se encontró sidebar de filtros")

    # Buscar cualquier mención de filtros en todo el documento
    print("\n=== BÚSQUEDA GENERAL DE FILTROS ===")

    all_filter_mentions = soup.find_all(text=re.compile(r'(?i)(categoría|marca|tipo|contenido|envase|sabor|elaboración|origen|formato|variedad|cantidad|presentación)'))

    unique_filters = set()
    for mention in all_filter_mentions:
        text = mention.strip()
        if text and len(text) > 1:
            unique_filters.add(text)

    print(f"Filtros únicos encontrados en todo el documento ({len(unique_filters)}):")
    for filter_name in sorted(unique_filters):
        print(f"  - {filter_name}")

if __name__ == "__main__":
    analyze_almacen_filters()
