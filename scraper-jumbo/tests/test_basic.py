"""
Tests básicos para Scraper Jumbo
"""

import pytest
import sys
from pathlib import Path

# Agregar src al path para importar módulos
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config import load_config, setup_logging
from src.scraper import JumboScraper


class TestConfig:
    """Tests para el módulo de configuración"""

    def test_load_config(self):
        """Test carga de configuración"""
        config = load_config()
        assert isinstance(config, dict)
        assert 'site_url' in config
        assert 'timeout' in config

    def test_config_validation(self):
        """Test validación de configuración"""
        config = load_config()

        # Validar campos requeridos
        required_fields = ['site_url', 'output_file', 'max_retries', 'timeout']
        for field in required_fields:
            assert field in config, f"Falta campo requerido: {field}"

        # Validar tipos
        assert isinstance(config['timeout'], int)
        assert config['timeout'] > 0


class TestScraper:
    """Tests para el módulo scraper"""

    def test_scraper_initialization(self):
        """Test inicialización del scraper"""
        scraper = JumboScraper()
        assert scraper.session is not None
        assert 'User-Agent' in scraper.session.headers
        scraper.close()

    def test_headers_setup(self):
        """Test configuración de headers"""
        scraper = JumboScraper()
        headers = scraper._get_default_headers()

        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert headers['Accept'].startswith('text/html')
        scraper.close()


class TestExtractor:
    """Tests para el módulo extractor"""

    def test_validate_category_url(self):
        """Test validación de URLs de categorías"""
        from src.extractor import validate_category_url

        # URLs válidas
        assert validate_category_url("https://www.jumbo.com.ar/electro")
        assert validate_category_url("https://www.jumbo.com.ar/hogar-y-textil")

        # URLs inválidas
        assert not validate_category_url("https://www.jumbo.com.ar/login")
        assert not validate_category_url("https://www.jumbo.com.ar/carrito")
        assert not validate_category_url("")
        assert not validate_category_url("http://otro-sitio.com")

    def test_clean_filter_name(self):
        """Test limpieza de nombres de filtros"""
        from src.extractor import clean_filter_name

        # Casos normales
        assert clean_filter_name("Color Azul") == "Color Azul"
        assert clean_filter_name("Tamaño  Grande  ") == "Tamaño Grande"

        # Casos con caracteres especiales
        assert clean_filter_name("Color (Azul)") == "Color Azul"
        assert clean_filter_name("Tamaño-Grande") == "Tamaño-Grande"

        # Casos edge
        assert clean_filter_name("") == ""
        assert clean_filter_name("   ") == ""


if __name__ == "__main__":
    # Ejecutar tests básicos
    print("🧪 Ejecutando tests básicos...")

    # Test configuración
    try:
        config = load_config()
        print("✅ Configuración cargada correctamente")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")

    # Test scraper
    try:
        scraper = JumboScraper()
        print("✅ Scraper inicializado correctamente")
        scraper.close()
    except Exception as e:
        print(f"❌ Error en scraper: {e}")

    print("🎉 Tests básicos completados")
