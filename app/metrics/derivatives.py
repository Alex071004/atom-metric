"""Вычисление производных для дискретных данных."""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class DerivativeCalculator:
    """
    Калькулятор производных для дискретных функций.
    Производная = (y[i+1] - y[i]) / (x[i+1] - x[i])
    """
    
    def __init__(self, use_smoothing: bool = False, interpolation_points: int = 5):
        self.use_smoothing = use_smoothing
        self.interpolation_points = interpolation_points
    
    def calculate_derivatives(self, values: List[int], dates: Optional[List] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Вычисление производных методом конечных разностей.
        Возвращает (x_centers, derivative_values)
        где x_centers - средние точки между днями
        """
        x = np.arange(len(values))
        y = np.array(values) / config.CARS_COUNT  # на одну машину
        
        # Вычисляем производные в средних точках между днями
        x_centers = (x[:-1] + x[1:]) / 2
        derivatives = (y[1:] - y[:-1]) / (x[1:] - x[:-1])
        
        return x_centers, derivatives
    
    def calculate_angles_at_points(self, values: List[int], dates: Optional[List] = None) -> List[float]:
        """
        Вычисление производных в исходных точках (для обратной совместимости)
        """
        x = np.arange(len(values))
        y = np.array(values) / config.CARS_COUNT
        
        # Центральные разности для внутренних точек
        derivatives = np.zeros(len(values))
        
        if len(values) >= 2:
            # Левая граница - правая разность
            derivatives[0] = (y[1] - y[0]) / (x[1] - x[0])
            
            # Правые границы - левая разность
            derivatives[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])
            
            # Центральные разности для внутренних точек
            for i in range(1, len(values)-1):
                derivatives[i] = (y[i+1] - y[i-1]) / (x[i+1] - x[i-1])
        
        return derivatives.tolist()
    
    def sum_of_derivatives(self, data: pd.DataFrame) -> pd.Series:
        """
        Сумма производных всех тачпоинтов.
        """
        total_derivatives = None
        
        for tp in config.TOUCHPOINTS:
            x_centers, derivs = self.calculate_derivatives(data[tp].tolist(), data['date'].tolist())
            
            if total_derivatives is None:
                total_derivatives = derivs
            else:
                # Интерполируем до одинаковой длины если нужно
                if len(derivs) != len(total_derivatives):
                    # Берем минимальную длину
                    min_len = min(len(derivs), len(total_derivatives))
                    total_derivatives = total_derivatives[:min_len] + derivs[:min_len]
                else:
                    total_derivatives += derivs
        
        # Создаем Series с индексами как у исходных данных (приблизительно)
        result = pd.Series(total_derivatives, index=range(len(total_derivatives)))
        return result
