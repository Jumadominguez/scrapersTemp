"""
Configuración del Scraper Jumbo
Maneja la carga de configuración YAML y setup de logging
"""

import os
import yaml
import logging
from pathlib import Path


def load_config(config_path=None):
    """
    Carga la configuración desde archivo YAML

    Args:
        config_path (str, optional): Ruta al archivo de configuración

    Returns:
        dict: Configuración cargada
    """
    if config_path is None:
        # Ruta por defecto relativa al directorio del proyecto
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config" / "config.yaml"

    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

        # Validar configuración esencial
        required_keys = ['site_url', 'output_file', 'max_retries', 'timeout']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Configuración requerida faltante: {key}")

        return config

    except FileNotFoundError:
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error al parsear configuración YAML: {e}")


def setup_logging(config):
    """
    Configura el sistema de logging

    Args:
        config (dict): Configuración del proyecto
    """
    log_level = getattr(logging, config.get('log_level', 'INFO').upper())
    log_file = config.get('log_file', 'logs/scraper.log')

    # Crear directorio de logs si no existe
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configurar logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # Configurar logger específico para el scraper
    logger = logging.getLogger('scraper_jumbo')
    logger.setLevel(log_level)

    return logger


def get_project_root():
    """
    Obtiene la ruta raíz del proyecto

    Returns:
        Path: Ruta raíz del proyecto
    """
    return Path(__file__).parent.parent


def validate_config(config):
    """
    Valida la configuración cargada

    Args:
        config (dict): Configuración a validar

    Raises:
        ValueError: Si la configuración es inválida
    """
    # Validar URLs
    if not config['site_url'].startswith('https://'):
        raise ValueError("site_url debe ser una URL HTTPS válida")

    # Validar timeouts
    if config['timeout'] < 1:
        raise ValueError("timeout debe ser al menos 1 segundo")

    # Validar delays
    if config['delay_between_requests'] < 0:
        raise ValueError("delay_between_requests no puede ser negativo")

    # Validar log level
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if config['log_level'].upper() not in valid_levels:
        raise ValueError(f"log_level debe ser uno de: {valid_levels}")


# Configuración global
CONFIG = None
LOGGER = None


def initialize_config():
    """
    Inicializa la configuración global del proyecto
    """
    global CONFIG, LOGGER

    if CONFIG is None:
        CONFIG = load_config()
        validate_config(CONFIG)

    if LOGGER is None:
        LOGGER = setup_logging(CONFIG)

    return CONFIG, LOGGER


# Función de conveniencia para obtener configuración
def get_config():
    """Obtiene la configuración global"""
    if CONFIG is None:
        initialize_config()
    return CONFIG


def get_logger():
    """Obtiene el logger global"""
    if LOGGER is None:
        initialize_config()
    return LOGGER
