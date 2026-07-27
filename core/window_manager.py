# core/window_manager.py
import os
import subprocess
import time
import pygetwindow as gw
import logging

class WindowManager:
    def __init__(self, config: dict):
        """
        Inicializa el gestor con la configuración específica de la aplicación.
        
        :param config: Diccionario con las claves:
                       - executable_path: Ruta al .exe
                       - process_name: Nombre del proceso (ej. 'x2goclient.exe')
                       - window_title_regex: Texto o regex del título de la ventana
        """
        self.executable_path = config.get("executable_path")
        self.process_name = config.get("process_name")
        self.window_title = config.get("window_title_regex")
        self.logger = logging.getLogger("RPA.WindowManager")

    def find_window(self) -> gw.Window:
        """Busca la ventana por título parcial. Retorna el objeto Window o None."""
        try:
            # gw.getWindowsWithTitle busca coincidencias parciales en el título
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                # Retornamos la primera coincidencia activa
                return windows[0]
        except Exception as e:
            self.logger.error(f"Error buscando ventana: {e}")
        return None

    def is_process_running(self) -> bool:
        """Verifica si el proceso está corriendo en Windows usando tasklist."""
        try:
            # Filtramos por el nombre del proceso
            command = f'tasklist /FI "IMAGENAME eq {self.process_name}"'
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            return self.process_name.lower() in result.stdout.lower()
        except Exception as e:
            self.logger.error(f"Error verificando proceso: {e}")
            return False

    def kill_process(self):
        """Fuerza el cierre de la aplicación."""
        self.logger.warning(f"Terminando proceso {self.process_name} a la fuerza (taskkill).")
        try:
            os.system(f'taskkill /F /IM {self.process_name} >nul 2>&1')
            time.sleep(2) # Tiempo de gracia para que Windows libere los recursos
        except Exception as e:
            self.logger.error(f"Error matando proceso: {e}")

    def start_process(self):
        """Inicia la aplicación objetivo."""
        if not self.executable_path or not os.path.exists(self.executable_path):
            raise FileNotFoundError(f"Ejecutable no encontrado: {self.executable_path}")
        
        self.logger.info(f"Iniciando aplicación: {self.executable_path}")
        # Usamos Popen para que no bloquee el script
        subprocess.Popen([self.executable_path])
        time.sleep(3) # Tiempo estándar de carga de la UI antes de buscar la ventana

    def force_focus(self) -> bool:
        """Trae la ventana al frente y la maximiza. Esencial antes de usar pyautogui."""
        window = self.find_window()
        if window:
            try:
                if window.isMinimized:
                    window.restore()
                window.activate()
                window.maximize()
                time.sleep(0.5) # Pequeña pausa para que el SO procese el foco
                self.logger.info("Foco forzado exitosamente.")
                return True
            except Exception as e:
                self.logger.error(f"Error al forzar foco: {e}. La ventana podría estar colgada.")
                return False
        return False

    def ensure_app_ready(self, max_retries: int = 2) -> bool:
        """
        Orquestación de alto nivel: Asegura que la app esté corriendo, visible y con foco.
        Si algo falla, intenta reiniciarla hasta max_retries.
        """
        retries = 0
        while retries <= max_retries:
            if self.force_focus():
                return True
            
            # Si no hay foco, verificamos si el proceso siquiera existe
            self.logger.warning(f"Ventana no enfocable. Intento {retries+1}/{max_retries+1}.")
            if self.is_process_running():
                self.logger.info("Proceso corre pero sin ventana visible. Matando proceso zombi...")
                self.kill_process()
            
            # Relanzamos
            self.start_process()
            retries += 1
            
        self.logger.critical("No se pudo establecer la aplicación lista tras múltiples intentos.")
        return False