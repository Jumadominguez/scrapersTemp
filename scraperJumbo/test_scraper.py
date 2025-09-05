#!/usr/bin/env python3
"""
Script de prueba rápida para verificar el funcionamiento del scraper
"""

import sys
import os
from pathlib import Path

# Agregar el directorio actual al path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from scraper_jumbo import JumboScraper

def test_scraper():
    """Prueba básica del scraper"""
    print("🧪 Probando Scraper de Jumbo...")
    print("=" * 40)

    scraper = JumboScraper()

    # Probar solo con una categoría para verificar funcionamiento
    test_category = ("Electro", "https://www.jumbo.com.ar/electro")

    print(f"📊 Probando con categoría: {test_category[0]}")
    print(f"🔗 URL: {test_category[1]}")
    print("-" * 40)

    try:
        filters = scraper.extract_filter_titles(test_category[1], test_category[0])

        print("✅ Extracción exitosa!")
        print(f"📊 Total de filtros encontrados: {len(filters)}")
        print("\n🔍 Filtros extraídos:")
        print("-" * 20)

        if filters:
            for i, filter_name in enumerate(filters[:10], 1):
                print("2")
            if len(filters) > 10:
                print(f"   ... y {len(filters) - 10} filtros más")
        else:
            print("   No se encontraron filtros")

        print("\n✅ Prueba completada exitosamente!")

    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    success = test_scraper()
    sys.exit(0 if success else 1)
