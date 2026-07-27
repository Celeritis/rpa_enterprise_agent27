# core/window_manager.py
import os
import subprocess
import time
import pygetwindow as gw
import pyautogui
import logging
from datetime import datetime

class WindowManager:
    def __init__(self, config: dict):
        self.executable_path = config.get("executable_path")
        self.process_name = config.get("process_name")
        self.window_title = config.get("window_title_regex")
        self.logger = logging.getLogger("RPA.WindowManager")

    def find_window(self) -> gw.Window:
        """Busca la ventana por título parcial (ignorando mayúsculas/minúsculas)."""
        try:
            # Iteramos sobre todas las ventanas abiertas en Windows
            for window in gw.getAllWindows():
                if window.title and self.window_title.lower() in window.title.lower():
                    # Verificamos que la ventana tenga tamaño (no esté oculta)
                    if window.width > 0 and window.height > 0:
                        return window
        except Exception as e:
            self.logger.error(f"Error buscando ventana: {e}")
        return None

    def is_process_running(self) -> bool:
        try:
            command = f'tasklist /FI "IMAGENAME eq {self.process_name}"'
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            return self.process_name.lower() in result.stdout.lower()
        except Exception as e:
            self.logger.error(f"Error verificando proceso: {e}")
            return False

    def kill_process(self):
        self.logger.warning(f"Terminando proceso {self.process_name} a la fuerza (taskkill).")
        try:
            os.system(f'taskkill /F /IM {self.process_name} >nul 2>&1')
            time.sleep(2)
        except Exception as e:
            self.logger.error(f"Error matando proceso: {e}")

    def start_process(self):
        if not self.executable_path or not os.path.exists(self.executable_path):
            raise FileNotFoundError(f"Ejecutable no encontrado: {self.executable_path}")
        
        self.logger.info(f"Iniciando aplicación: {self.executable_path}")
        subprocess.Popen([self.executable_path])
        # Aumentamos el tiempo de espera a 6 segundos. X2GoClient es lento en Windows.
        time.sleep(6) 

    def force_focus(self) -> bool:
        window = self.find_window()
        if window:
            try:
                if window.isMinimized:
                    window.restore()
                window.activate()
                window.maximize()
                time.sleep(0.5)
                self.logger.info(f"Foco forzado exitosamente en: {window.title}")
                return True
            except Exception as e:
                self.logger.error(f"Error al forzar foco: {e}. La ventana podría estar colgada.")
                return False
        return False

    def _capture_evidence(self, prefix: str):
        """Captura pantalla cuando el gestor de ventanas falla."""
        os.makedirs("data/output/evidences", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join("data/output/evidences", f"{prefix}_{timestamp}.png")
        pyautogui.screenshot(filepath)
        self.logger.info(f"[EVIDENCIA GUARDADA] Fallo de ventana registrado en: {filepath}")

    def ensure_app_ready(self, max_retries: int = 2) -> bool:
        retries = 0
        while retries <= max_retries:
            if self.force_focus():
                return True
            
            self.logger.warning(f"Ventana no enfocable. Intento {retries+1}/{max_retries+1}.")
            if self.is_process_running():
                self.logger.info("Proceso corre pero sin ventana visible. Matando proceso zombi...")
                self.kill_process()
            
            try:
                self.start_process()
            except FileNotFoundError as e:
                self.logger.critical(e)
                return False
                
            retries += 1
            
        self.logger.critical("No se pudo establecer la aplicación lista tras múltiples intentos.")
        self._capture_evidence("window_manager_failure")
        return False