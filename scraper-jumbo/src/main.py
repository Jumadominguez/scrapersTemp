#!/usr/bin/env python3
"""
Scraper Jumbo - Extracción automática de filtros
Punto de entrada principal del script

Uso:
    python main.py
    python main.py --config /path/to/config.yaml
    python main.py --verbose
    python main.py --test-connection
    python main.py --site-info
    python main.py --validate-content
"""

import sys
import argparse
import logging
from pathlib import Path

# Agregar el directorio src al path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from config import initialize_config, get_logger
from scraper import JumboScraper
from extractor import extract_categories, extract_filters_from_category
from generator import generate_markdown


def parse_arguments():
    """Parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Scraper Jumbo - Extracción de filtros')

    parser.add_argument(
        '--config',
        type=str,
        help='Ruta al archivo de configuración YAML'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verbose con más información de debug'
    )

    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Solo probar conexión al sitio web'
    )

    parser.add_argument(
        '--site-info',
        action='store_true',
        help='Mostrar información del sitio web'
    )

    parser.add_argument(
        '--validate-content',
        action='store_true',
        help='Validar contenido del sitio web'
    )

    return parser.parse_args()


def test_connection(scraper, logger):
    """Prueba la conexión básica al sitio web"""
    logger.info("Probando conexión a Jumbo...")

    try:
        content = scraper.get_page("https://www.jumbo.com.ar")
        if content and "Jumbo" in content:
            logger.info("✅ Conexión exitosa a Jumbo")
            return True
        else:
            logger.error("❌ Contenido no válido recibido")
            return False
    except Exception as e:
        logger.error(f"❌ Error de conexión: {e}")
        return False


def main():
    """Función principal del scraper"""
    args = parse_arguments()

    # Inicializar configuración y logging
    try:
        config, logger = initialize_config()
        logger.info("🚀 Iniciando Scraper Jumbo v1.0")
        logger.info(f"📁 Directorio de trabajo: {project_root}")

    except Exception as e:
        print(f"❌ Error al inicializar configuración: {e}")
        sys.exit(1)

    # Override log level si se especifica verbose
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info("🔍 Modo verbose activado")

    # Crear instancia del scraper
    try:
        scraper = JumboScraper()
        logger.info("🔧 Scraper inicializado correctamente")
    except Exception as e:
        logger.error(f"❌ Error al inicializar scraper: {e}")
        sys.exit(1)

    # Manejar opciones específicas de la Etapa 2
    if args.test_connection:
        success = scraper.test_connection()
        sys.exit(0 if success else 1)

    if args.site_info:
        site_info = scraper.get_site_info()
        logger.info("📊 Información del sitio:")
        for key, value in site_info.items():
            logger.info(f"  {key}: {value}")
        sys.exit(0)

    if args.validate_content:
        content = scraper.get_page(config['site_url'])
        if content:
            is_valid = scraper._validate_jumbo_content(content)
            logger.info(f"✅ Contenido válido: {is_valid}")
            sys.exit(0 if is_valid else 1)
        else:
            logger.error("❌ No se pudo obtener contenido para validar")
            sys.exit(1)

    # Flujo principal de extracción
    try:
        logger.info("🌐 Obteniendo página principal...")

        # 1. Obtener página principal
        main_page_content = scraper.get_page(config['site_url'])
        if not main_page_content:
            logger.error("❌ No se pudo obtener la página principal")
            sys.exit(1)

        # 2. Extraer categorías
        logger.info("📂 Extrayendo categorías...")
        categories = extract_categories(main_page_content)

        if not categories:
            logger.warning("⚠️ No se encontraron categorías")
            sys.exit(1)

        logger.info(f"📋 Encontradas {len(categories)} categorías")

        # 3. Procesar cada categoría
        for i, category in enumerate(categories, 1):
            logger.info(f"🔍 Procesando categoría {i}/{len(categories)}: {category['name']}")

            # Extraer filtros de la categoría
            filters = extract_filters_from_category(scraper, category['url'])
            category['filters'] = filters

            logger.info(f"✅ Extraídos {len(filters)} filtros para {category['name']}")

        # 4. Generar archivo Markdown
        logger.info("📝 Generando archivo Markdown...")
        output_path = project_root / config['output_file']
        generate_markdown(categories, str(output_path))

        logger.info(f"✅ Archivo generado: {output_path}")
        logger.info("🎉 ¡Extracción completada exitosamente!")

    except KeyboardInterrupt:
        logger.info("⏹️ Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error durante la extracción: {e}")
        logger.debug("Traceback completo:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
