# core/dynamic_waiter.py
import time
import os
from datetime import datetime
from core.vision_engine import VisionEngine
from PIL import ImageGrab

class TimeoutException(Exception):
    """Excepción personalizada para cuando una espera dinámica excede el tiempo."""
    pass

class DynamicWaiter:
    def __init__(self, vision_engine: VisionEngine, evidence_path="data/output/evidences"):
        self.vision = vision_engine
        self.evidence_path = evidence_path
        os.makedirs(self.evidence_path, exist_ok=True)

    def wait_for_image(self, image_path: str, timeout: int = 10, interval: float = 0.5, confidence: float = 0.8) -> bool:
        """
        Espera dinámica: Busca una imagen en pantalla hasta que aparezca o se agote el timeout.
        
        :param image_path: Ruta al archivo de la imagen ancla (asset).
        :param timeout: Tiempo máximo de espera en segundos.
        :param interval: Intervalo de búsqueda en segundos.
        :param confidence: Umbral de coincidencia (0.0 a 1.0).
        :return: True si la imagen fue encontrada.
        :raises TimeoutException: Si la imagen no aparece en el tiempo estimado.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.vision.find_on_screen(image_path, confidence):
                return True
            time.sleep(interval)
            
        # Si llegamos aquí, el timeout expiró. Capturamos evidencia del fallo.
        self._capture_evidence(f"timeout_{os.path.basename(image_path)}")
        raise TimeoutException(f"Timeout esperando imagen: {image_path} tras {timeout} segundos.")

    def wait_for_image_to_disappear(self, image_path: str, timeout: int = 10, interval: float = 0.5, confidence: float = 0.8) -> bool:
        """
        Espera a que una imagen desaparezca de la pantalla (ej. un popup de carga).
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.vision.find_on_screen(image_path, confidence):
                return True
            time.sleep(interval)
            
        self._capture_evidence(f"stuck_{os.path.basename(image_path)}")
        raise TimeoutException(f"La imagen {image_path} no desapareció tras {timeout} segundos. Posible cuelgue del ERP.")

    def _capture_evidence(self, prefix: str):
        """Guarda una captura de pantalla para auditar por qué falló la espera."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        filepath = os.path.join(self.evidence_path, filename)
        
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        print(f"[EVIDENCIA GUARDADA] Fallo registrado en: {filepath}")