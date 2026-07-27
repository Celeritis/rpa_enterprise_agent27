# core/session_manager.py
import json
import os
import logging
import time
import pyautogui
from core.vision_engine import VisionEngine
from core.dynamic_waiter import DynamicWaiter, TimeoutException
from core.window_manager import WindowManager

class SessionManager:
    def __init__(self, config_path: str):
        self.logger = logging.getLogger("RPA.SessionManager")
        self.config_path = config_path
        self.config = self._load_json(config_path)
        self.base_dir = os.getcwd() # Asume ejecución desde la raíz del proyecto
        
        # Inicializar componentes del Core
        self.vision = VisionEngine()
        self.waiter = DynamicWaiter(self.vision)
        self.window_manager = WindowManager(self.config.get("process_config", {}))
        
        self.logger.info(f"SessionManager inicializado para: {self.config.get('app_name')}")

    def _load_json(self, path: str) -> dict:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {path}")
        # Usamos utf-8-sig para ignorar el BOM de Windows de forma segura
        with open(path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)

    def start_session(self):
        """Asegura que la app esté corriendo y las precondiciones visuales se cumplan."""
        self.logger.info("Iniciando preparación del entorno...")
        
        # 1. Asegurar que la ventana exista y tenga foco
        if not self.window_manager.ensure_app_ready():
            raise RuntimeError("No se pudo establecer la ventana de la aplicación. Abortando.")
        
        # 2. Verificar anclas globales (Ej: ¿El ERP realmente cargó?)
        anchor_key = "erp_main_menu_loaded"
        anchor_path = self.config.get("global_anchors", {}).get(anchor_key)
        
        if anchor_path:
            full_path = os.path.join(self.base_dir, anchor_path)
            startup_timeout = self.config.get("process_config", {}).get("startup_wait_sec", 20)
            self.logger.info(f"Esperando ancla de sistema: {anchor_key}")
            self.waiter.wait_for_image(full_path, timeout=startup_timeout)
            self.logger.info("Sistema cargado y listo.")

    def execute_flow(self, flow_path: str):
        """Ejecuta los pasos definidos en el archivo de flujo JSON."""
        flow_data = self._load_json(flow_path)
        steps = flow_data.get("steps", [])
        self.logger.info(f"Ejecutando flujo: {flow_data.get('flow_name')} ({len(steps)} pasos)")

        for step in steps:
            step_id = step.get("id")
            desc = step.get("description", "Sin descripción")
            action = step.get("action_type")
            
            self.logger.info(f"--- Ejecutando Paso {step_id}: {desc} ---")
            
            try:
                self._dispatch_action(action, step)
            except TimeoutException as e:
                self.logger.error(f"Fallo en Paso {step_id}: {e}")
                self.logger.warning("Ejecución del flujo interrumpida por timeout visual.")
                # Aquí se podría implementar lógica de reintento o recuperación
                break
            except Exception as e:
                self.logger.critical(f"Error inesperado en Paso {step_id}: {e}")
                break

    def _dispatch_action(self, action: str, step: dict):
        """Enrutador de acciones. Aquí se decide qué hacer según el JSON."""
        confidence = self.config.get("vision_config", {}).get("default_confidence", 0.8)
        
        if action == "click_image":
            target = os.path.join(self.base_dir, step["target_image"])
            coords = self.vision.find_on_screen(target, confidence)
            if coords:
                self.logger.debug(f"Imagen encontrada en {coords}. Haciendo click.")
                pyautogui.click(coords)
                # Espera micro después de click para que el UI reaccione
                time.sleep(0.5) 
            else:
                raise TimeoutException(f"No se encontró la imagen para click: {target}")
                
        elif action == "wait_for_image":
            target = os.path.join(self.base_dir, step["target_image"])
            timeout_key = step.get("timeout_key", "medium_action")
            timeout = self.config.get("timeouts", {}).get(timeout_key, 10)
            self.waiter.wait_for_image(target, timeout=timeout, confidence=confidence)
            
        elif action == "load_data":
            file_key = step.get("target_file")
            file_path = self.config.get("flow_data", {}).get(file_key) or step.get("target_file")
            self.logger.info(f"Cargando datos desde: {file_path}")
            # TODO: Implementar lectura de CSV y preparar iteración de datos
            
        else:
            self.logger.warning(f"Acción no reconocida: {action}")

    def __enter__(self):
        """Permite usar 'with SessionManager(...) as session:'"""
        self.start_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Limpieza al finalizar el script."""
        if exc_type:
            self.logger.error("La sesión terminó con errores.")
        else:
            self.logger.info("Flujo completado y sesión finalizada limpiamente.")
        
        # Aquí podríamos cerrar la app si la config lo dicta, o simplemente liberar recursos.