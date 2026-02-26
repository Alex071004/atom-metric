"""Упрощенное вычисление производных."""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class DerivativeCalculator:
    """Простой калькулятор производных."""
    
    def __init__(self):
        pass
    
    def calculate_derivatives(self, values: List[int]) -> List[float]:
        """
        Вычисление производных методом центральных разностей.
        Результат на одну машину.
        """
        y = np.array(values) / config.CARS_COUNT
        x = np.arange(len(y))
        
        # Производная через центральные разности
        derivatives = np.zeros_like(y)
        
        if len(y) >= 3:
            # Центральные разности для внутренних точек
            derivatives[1:-1] = (y[2:] - y[:-2]) / (x[2:] - x[:-2])
            
            # Граничные точки (линейная аппроксимация)
            derivatives[0] = (y[1] - y[0]) / (x[1] - x[0])
            derivatives[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])
        elif len(y) == 2:
            derivatives[0] = (y[1] - y[0]) / (x[1] - x[0])
            derivatives[1] = derivatives[0]
        
        return derivatives.tolist()
    
    def sum_of_derivatives(self, data: pd.DataFrame) -> pd.Series:
        """Сумма производных всех тачпоинтов."""
        total = np.zeros(len(data))
        
        for tp in config.TOUCHPOINTS:
            deriv = self.calculate_derivatives(data[tp].tolist())
            total += np.array(deriv)
        
        return pd.Series(total, index=data.index)
