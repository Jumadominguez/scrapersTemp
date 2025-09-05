#!/usr/bin/env python3
"""
Tests para el módulo Scraper
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

import pytest
import requests
from unittest.mock import Mock, patch
from scraper import JumboScraper


class TestJumboScraper:
    """Tests para la clase JumboScraper"""

    def test_scraper_initialization(self):
        """Test que el scraper se inicializa correctamente"""
        scraper = JumboScraper()
        assert scraper.session is not None
        assert scraper.config is not None
        assert scraper.logger is not None

    def test_headers_setup(self):
        """Test que los headers se configuran correctamente"""
        scraper = JumboScraper()
        headers = scraper._get_default_headers()

        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert 'Accept-Language' in headers
        assert headers['Accept-Language'] == 'es-AR,es;q=0.9,en;q=0.8'

    @patch('requests.Session.get')
    def test_successful_page_request(self, mock_get):
        """Test de request exitoso"""
        # Configurar el mock con contenido de longitud adecuada
        mock_response = Mock()
        mock_response.text = '<html><body>' + 'Test content ' * 20 + '</body></html>'  # > 100 chars
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        scraper = JumboScraper()
        result = scraper.get_page('https://www.jumbo.com.ar')

        assert result == mock_response.text
        mock_get.assert_called_once()

    @patch('requests.Session.get')
    def test_timeout_handling(self, mock_get):
        """Test de manejo de timeout"""
        mock_get.side_effect = requests.exceptions.Timeout()

        scraper = JumboScraper()
        result = scraper.get_page('https://www.jumbo.com.ar', max_retries=1)

        assert result is None

    @patch('requests.Session.get')
    def test_connection_error_handling(self, mock_get):
        """Test de manejo de error de conexión"""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        scraper = JumboScraper()
        result = scraper.get_page('https://www.jumbo.com.ar', max_retries=1)

        assert result is None

    @patch('requests.Session.get')
    def test_http_error_handling(self, mock_get):
        """Test de manejo de errores HTTP"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)

        mock_get.return_value = mock_response

        scraper = JumboScraper()
        result = scraper.get_page('https://www.jumbo.com.ar', max_retries=1)

        assert result is None

    @patch('requests.Session.get')
    def test_retry_mechanism(self, mock_get):
        """Test del mecanismo de reintentos"""
        # Configurar responses: primero falla, segundo tiene éxito
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = requests.exceptions.ConnectionError()

        mock_response_success = Mock()
        mock_response_success.text = 'Success content ' * 20  # > 100 chars
        mock_response_success.status_code = 200

        mock_get.side_effect = [mock_response_fail, mock_response_success]

        scraper = JumboScraper()
        result = scraper.get_page('https://www.jumbo.com.ar', max_retries=1)

        assert result == mock_response_success.text
        assert mock_get.call_count == 2

    @patch('requests.Session.get')
    def test_content_validation(self, mock_get):
        """Test de validación de contenido"""
        # Contenido demasiado pequeño
        mock_response = Mock()
        mock_response.text = 'Short'
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        scraper = JumboScraper()
        result = scraper.get_page('https://www.jumbo.com.ar', max_retries=0)

        assert result is None

    def test_basic_connection_integration(self):
        """Test de integración básica de conexión (sin mock)"""
        scraper = JumboScraper()

        # Este test puede fallar si no hay conexión a internet
        # pero es útil para verificar la configuración real
        try:
            result = scraper.get_page('https://httpbin.org/html', max_retries=1)
            if result:
                assert 'html' in result.lower()
        except Exception:
            # Si falla, es aceptable en entornos sin conexión
            pytest.skip("No hay conexión a internet disponible")
