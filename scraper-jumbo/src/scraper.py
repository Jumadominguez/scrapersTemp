"""
Módulo Scraper - Manejo de conexiones HTTP
"""

import time
import requests
from typing import Optional, Dict, Any
from config import get_config, get_logger


class JumboScraper:
    """
    Cliente HTTP para scraping de Jumbo
    Maneja conexiones, reintentos y rate limiting
    """

    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()
        self.session = requests.Session()
        self.session.headers.update(self._get_default_headers())

        self.logger.info("🔧 JumboScraper inicializado")

    def _get_default_headers(self) -> Dict[str, str]:
        """Obtiene los headers por defecto para las requests"""
        return {
            'User-Agent': self.config['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def get_page(self, url: str, max_retries: Optional[int] = None) -> Optional[str]:
        """
        Obtiene el contenido de una página web con manejo de errores

        Args:
            url (str): URL de la página a obtener
            max_retries (int, optional): Número máximo de reintentos

        Returns:
            Optional[str]: Contenido HTML de la página o None si falla
        """
        if max_retries is None:
            max_retries = self.config['max_retries']

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                self.logger.debug(f"🌐 Intentando acceder a: {url} (intento {attempt + 1})")

                response = self.session.get(
                    url,
                    timeout=self.config['timeout'],
                    allow_redirects=True
                )

                response.raise_for_status()

                # Verificar que el contenido sea válido
                if len(response.text) < 100:
                    raise ValueError("Contenido de respuesta demasiado pequeño")

                self.logger.debug(f"✅ Página obtenida exitosamente ({len(response.text)} caracteres)")
                return response.text

            except requests.exceptions.Timeout:
                last_exception = f"Timeout después de {self.config['timeout']} segundos"
                self.logger.warning(f"⏱️ {last_exception}")
            except requests.exceptions.ConnectionError:
                last_exception = "Error de conexión"
                self.logger.warning(f"🔌 {last_exception}")
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                last_exception = f"Error HTTP {status_code}"
                self.logger.warning(f"🌐 {last_exception}")

                # No reintentar para errores 4xx (excepto 429)
                if 400 <= status_code < 500 and status_code != 429:
                    break
            except Exception as e:
                last_exception = f"Error inesperado: {str(e)}"
                self.logger.warning(f"❌ {last_exception}")

            # Esperar antes del siguiente intento
            if attempt < max_retries:
                delay = self.config['delay_between_requests'] * (attempt + 1)
                self.logger.info(f"⏳ Esperando {delay} segundos antes del siguiente intento...")
                time.sleep(delay)

        self.logger.error(f"❌ Fallaron todos los intentos para {url}. Último error: {last_exception}")
        return None

    def get_page_with_retry(self, url: str, custom_delay: Optional[float] = None) -> Optional[str]:
        """
        Obtiene una página con delay personalizado entre requests

        Args:
            url (str): URL de la página
            custom_delay (float, optional): Delay personalizado en segundos

        Returns:
            Optional[str]: Contenido de la página
        """
        result = self.get_page(url)

        # Aplicar delay personalizado si se especifica
        if custom_delay:
            self.logger.debug(f"⏳ Aplicando delay personalizado: {custom_delay}s")
            time.sleep(custom_delay)

        return result

    def test_connection(self) -> bool:
        """
        Prueba la conexión básica al sitio de Jumbo

        Returns:
            bool: True si la conexión es exitosa
        """
        self.logger.info("🔍 Probando conexión a Jumbo...")

        try:
            content = self.get_page(self.config['site_url'])

            if content and self._validate_jumbo_content(content):
                self.logger.info("✅ Conexión exitosa a Jumbo")
                return True
            else:
                self.logger.error("❌ Conexión fallida o contenido inválido")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error durante la prueba de conexión: {e}")
            return False

    def _validate_jumbo_content(self, content: str) -> bool:
        """
        Valida que el contenido pertenece al sitio de Jumbo

        Args:
            content (str): Contenido HTML a validar

        Returns:
            bool: True si el contenido es válido
        """
        # Validaciones básicas del sitio de Jumbo
        validations = [
            "jumbo" in content.lower(),
            "html" in content.lower(),  # Debe ser HTML válido
            len(content) > 1000  # Contenido debe ser sustancial
        ]

        return all(validations)

    def get_site_info(self) -> Dict[str, Any]:
        """
        Obtiene información básica del sitio

        Returns:
            Dict[str, Any]: Información del sitio
        """
        self.logger.info("📊 Obteniendo información del sitio...")

        content = self.get_page(self.config['site_url'])

        if not content:
            return {"error": "No se pudo acceder al sitio"}

        return {
            "url": self.config['site_url'],
            "content_length": len(content),
            "has_jumbo": "jumbo" in content.lower(),
            "title": self._extract_title(content),
            "status": "accessible" if self._validate_jumbo_content(content) else "invalid_content"
        }

    def _extract_title(self, content: str) -> str:
        """
        Extrae el título de la página del contenido HTML

        Args:
            content (str): Contenido HTML

        Returns:
            str: Título de la página
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            title_tag = soup.find('title')
            return title_tag.text.strip() if title_tag else "Sin título"
        except Exception:
            return "Error al extraer título"

    def close(self):
        """Cierra la sesión HTTP"""
        self.session.close()
        self.logger.info("🔌 Sesión HTTP cerrada")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
