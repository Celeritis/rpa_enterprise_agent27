# main.py
import logging
import os
import sys
from datetime import datetime
from core.session_manager import SessionManager

def setup_logging():
    """Configura el sistema de logs para consola y archivo."""
    log_dir = "data/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Nombre de archivo con timestamp para no sobreescribir logs viejos
    log_file = os.path.join(log_dir, f"rpa_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout) # También imprime en consola
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger("RPA.Main")
    
    # Rutas a los archivos de configuración de la App X2GoClient
    config_path = "apps/x2goclient_erp_legacy/config.json"
    flow_path = "apps/x2goclient_erp_legacy/flow_art_pro.json"
    
    logger.info("=== INICIANDO AGENTE RPA ENTERPRISE ===")
    
    try:
        # El Context Manager inicia la sesión (abre X2Go, verifica foco, busca anclas)
        with SessionManager(config_path) as session:
            # Una vez el entorno está listo, ejecuta el flujo de negocio
            session.execute_flow(flow_path)
            
        logger.info("=== EJECUCIÓN FINALIZADA EXITOSAMENTE ===")
        sys.exit(0) # Código de salida 0 = Éxito
            
    except RuntimeError as e:
        logger.critical(f"FALLO DE ENTORNO: {e}")
        logger.critical("El agente no pudo preparar la aplicación. Abortando.")
        sys.exit(1) # Código de salida 1 = Fallo
    except Exception as e:
        logger.critical(f"ERROR INESPERADO: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()