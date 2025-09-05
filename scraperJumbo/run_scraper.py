#!/usr/bin/env python3
"""
Script de ejecución simplificado para el scraper de Jumbo
"""

import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importar el scraper
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from scraper_jumbo import JumboScraper

def main():
    """Función principal de ejecución"""
    print("🚀 Iniciando Scraper de Jumbo...")
    print("=" * 50)

    try:
        # Crear instancia del scraper
        scraper = JumboScraper()

        # Ejecutar scraping
        print("📊 Scrapeando categorías...")
        results = scraper.scrape_all_categories()

        # Guardar resultados
        print("💾 Guardando resultados...")
        json_path, markdown_path = scraper.save_results(results, str(current_dir / "output"))

        # Mostrar resumen
        print("\n" + "=" * 50)
        print("✅ SCRAPING COMPLETADO!")
        print("=" * 50)
        print(f"📁 Resultados JSON: {json_path}")
        print(f"📄 Reporte Markdown: {markdown_path}")
        print("\n📊 RESUMEN POR CATEGORÍA:")
        print("-" * 30)

        for category, data in results.items():
            print("30")

        print("\n🎉 ¡Proceso terminado exitosamente!")

    except Exception as e:
        print(f"❌ Error durante la ejecución: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
