# core/vision_engine.py
import cv2
import numpy as np
import pyautogui
import os

class VisionEngine:
    def __init__(self):
        # Desactivamos el failsafe de pyautogui a nivel global si lo manejamos por separado,
        # pero lo mantenemos activo por seguridad (mover ratón a esquina superior izquierda aborta).
        pyautogui.FAILSAFE = True
        # Escalado de pantalla (útil si X2GO se ve en diferentes resoluciones)
        self.scale_factor = 1.0 

    def find_on_screen(self, image_path: str, confidence: float = 0.8) -> tuple or None:
        """
        Busca una imagen en la pantalla principal usando OpenCV.
        
        :param image_path: Ruta al asset (imagen a buscar).
        :param confidence: Umbral de coincidencia (0.0 a 1.0).
        :return: Tupla (x, y) con las coordenadas del centro de la imagen si se encuentra, si no None.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Asset no encontrado: {image_path}")

        # 1. Tomar captura de pantalla actual
        screenshot = pyautogui.screenshot()
        screen_np = np.array(screenshot)
        
        # Convertir RGB (PIL) a BGR (OpenCV)
        screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
        
        # 2. Cargar la imagen plantilla (asset)
        template = cv2.imread(image_path, cv2.IMREAD_COLOR)
        
        # 3. Ejecutar matchTemplate
        result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
        
        # 4. Filtrar por umbral de confianza
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            # Calcular el centro de la zona encontrada
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)
            
        return None

    def find_all_on_screen(self, image_path: str, confidence: float = 0.8) -> list:
        """
        Busca todas las ocurrencias de una imagen en pantalla.
        Útil si hay múltiples checkboxes o botones idénticos.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Asset no encontrado: {image_path}")

        screenshot = pyautogui.screenshot()
        screen_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template = cv2.imread(image_path, cv2.IMREAD_COLOR)
        
        result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
        
        # Encontrar todas las zonas que superan el umbral
        locations = np.where(result >= confidence)
        h, w = template.shape[:2]
        
        centers = []
        for pt in zip(*locations[::-1]):
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            centers.append((center_x, center_y))
            
        # Eliminar duplicados (OpenCV puede encontrar píxeles adyacentes)
        # TODO: Añadir lógica de agrupación si es necesario en el futuro.
        return centers