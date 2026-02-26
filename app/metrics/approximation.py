"""Упрощенная аппроксимация данных."""
import numpy as np
from typing import Tuple, List

class DataApproximator:
    """Простое сглаживание данных."""
    
    def __init__(self, window_size: int = 3):
        """
        window_size: размер окна для скользящего среднего (должен быть нечетным)
        """
        self.window_size = window_size if window_size % 2 == 1 else window_size + 1
    
    def smooth(self, y: List[float]) -> List[float]:
        """
        Сглаживание скользящим средним.
        """
        if len(y) < self.window_size:
            return y
        
        y = np.array(y)
        window = np.ones(self.window_size) / self.window_size
        smoothed = np.convolve(y, window, mode='same')
        
        # Корректировка краевых эффектов
        pad = self.window_size // 2
        smoothed[:pad] = y[:pad]
        smoothed[-pad:] = y[-pad:]
        
        return smoothed.tolist()
