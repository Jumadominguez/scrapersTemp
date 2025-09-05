"""
Módulo Generator - Generación del archivo Markdown
"""

import os
from datetime import datetime
from typing import List, Dict, Any
from config import get_logger, get_config


logger = get_logger()
config = get_config()


def generate_markdown(categories: List[Dict[str, Any]], output_file: str) -> bool:
    """
    Genera el archivo Markdown con todas las categorías y filtros

    Args:
        categories (List[Dict[str, Any]]): Lista de categorías con filtros
        output_file (str): Ruta del archivo de salida

    Returns:
        bool: True si se generó exitosamente
    """
    logger.info(f"📝 Generando archivo Markdown: {output_file}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Encabezado del archivo
            f.write("# Categorias\n")
            f.write("<!-- Generado automáticamente por Scraper Jumbo -->\n")
            f.write(f"<!-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->\n")
            f.write(f"<!-- Total de categorías: {len(categories)} -->\n\n")

            # Lista de categorías
            for i, category in enumerate(categories, 1):
                f.write(f"{i}. {category['name']}: {category['url']}\n")

            f.write("\n## Filtros por Categoría\n\n")

            # Sección de filtros por categoría
            for category in categories:
                f.write(f"### {category['name']}\n")

                filters = category.get('filters', [])
                total_filters = len(filters)

                f.write(f"**Total de filtros: {total_filters}**\n")
                f.write("-- FiltrosCategory\n")
                f.write("Categoría\n")
                f.write("Sub-Categoría\n")
                f.write("-- Tipo de producto\n")
                f.write("Tipo de Producto\n")
                f.write("-- Subfiltros\n")

                # Filtros específicos (excluyendo los base)
                for filter_name in filters[3:]:  # Saltar los 3 filtros base
                    f.write(f"{filter_name}\n")

                f.write("\n")

            # Pie de página con estadísticas
            total_filters_all = sum(len(cat.get('filters', [])) for cat in categories)
            f.write("---\n\n")
            f.write("**Estadísticas de la extracción:**\n")
            f.write(f"- Categorías procesadas: {len(categories)}\n")
            f.write(f"- Total de filtros: {total_filters_all}\n")
            f.write(f"- Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- Generado por: Scraper Jumbo v1.0\n")

        logger.info(f"✅ Archivo Markdown generado exitosamente: {output_file}")
        logger.info(f"📊 Estadísticas: {len(categories)} categorías, {total_filters_all} filtros totales")

        return True

    except Exception as e:
        logger.error(f"❌ Error al generar archivo Markdown: {e}")
        return False


def generate_summary_report(categories: List[Dict[str, Any]], output_dir: str = "reports") -> bool:
    """
    Genera un reporte resumen de la extracción

    Args:
        categories (List[Dict[str, Any]]): Lista de categorías procesadas
        output_dir (str): Directorio para el reporte

    Returns:
        bool: True si se generó exitosamente
    """
    logger.info("📊 Generando reporte resumen...")

    try:
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)

        report_file = os.path.join(output_dir, "extraction_report.txt")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("REPORTE DE EXTRACCIÓN - SCRAPER JUNBO\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"Fecha de extracción: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de categorías: {len(categories)}\n\n")

            # Estadísticas por categoría
            f.write("DETALLE POR CATEGORÍA:\n")
            f.write("-" * 30 + "\n")

            total_filters = 0
            for category in categories:
                filters_count = len(category.get('filters', []))
                total_filters += filters_count
                f.write(f"{category['name']}: {filters_count} filtros\n")

            f.write(f"\nTOTAL DE FILTROS: {total_filters}\n")
        logger.info(f"✅ Reporte generado: {report_file}")
        return True

    except Exception as e:
        logger.error(f"❌ Error al generar reporte: {e}")
        return False


def validate_generated_file(file_path: str) -> bool:
    """
    Valida que el archivo generado sea correcto

    Args:
        file_path (str): Ruta del archivo a validar

    Returns:
        bool: True si es válido
    """
    logger.info(f"🔍 Validando archivo generado: {file_path}")

    try:
        if not os.path.exists(file_path):
            logger.error("❌ Archivo no existe")
            return False

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Validaciones básicas
        if len(content) < 100:
            logger.error("❌ Archivo demasiado pequeño")
            return False

        if "# Categorias" not in content:
            logger.error("❌ Falta encabezado de categorías")
            return False

        if "## Filtros por Categoría" not in content:
            logger.error("❌ Falta sección de filtros")
            return False

        logger.info("✅ Archivo validado correctamente")
        return True

    except Exception as e:
        logger.error(f"❌ Error al validar archivo: {e}")
        return False
