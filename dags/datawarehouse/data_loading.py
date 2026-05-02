import json 
import logging
from datetime import date, datetime


# Crear logger para que Airflow registre mensajes en los logs del DAG
logger = logging.getLogger(__name__)


def load_path():
    # Obtener la fecha actual en formato YYYY-MM-DD
   today = date.today().strftime("%Y-%m-%d")
    # Construir la ruta del archivo JSON generado previamente
   file_path = f"/opt/airflow/data/video_stats_{today}.json"
    
   try:
       # Log informativo para debugging
        logger.info(f"Loading data from {today}")
        # Abrir el archivo JSON y cargarlo como objeto Python
        with open(file_path, "r", encoding="utf-8") as raw_data:
            data = json.load(raw_data)
            
        return data
            # Error si el archivo no existe
   except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
   except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {file_path}")
        raise       