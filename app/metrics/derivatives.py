"""Вычисление производных с прореживанием данных."""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class DerivativeCalculator:
    """Калькулятор производных с прореживанием данных."""
    
    def __init__(self, step: int = 5):
        """
        step: шаг прореживания (берем каждую step-ю точку)
        """
        self.step = step
    
    def calculate_derivatives(self, values: List[int]) -> List[float]:
        """
        Вычисление производных на прореженных данных.
        Возвращает массив той же длины, но с интерполированными значениями.
        """
        y = np.array(values) / config.CARS_COUNT
        x = np.arange(len(y))
        
        # Создаем массив для результатов
        derivatives = np.zeros_like(y)
        
        # Берем каждую step-ю точку для вычисления производных
        indices = list(range(0, len(y), self.step))
        
        # Если точек太少, добавляем последнюю
        if indices[-1] != len(y) - 1:
            indices.append(len(y) - 1)
        
        # Вычисляем производные только на выбранных точках
        deriv_at_indices = []
        for i in range(len(indices) - 1):
            idx1 = indices[i]
            idx2 = indices[i + 1]
            
            # Производная = (y2 - y1) / (x2 - x1)
            deriv = (y[idx2] - y[idx1]) / (x[idx2] - x[idx1])
            deriv_at_indices.append(deriv)
            
            # Заполняем все точки между idx1 и idx2 этим значением
            for j in range(idx1, idx2):
                derivatives[j] = deriv
        
        # Заполняем последний отрезок
        if len(indices) >= 2:
            last_deriv = deriv_at_indices[-1]
            for j in range(indices[-2], len(y)):
                derivatives[j] = last_deriv
        
        return derivatives.tolist()
    
    def sum_of_derivatives(self, data: pd.DataFrame) -> pd.Series:
        """Сумма производных всех тачпоинтов."""
        total = np.zeros(len(data))
        
        for tp in config.TOUCHPOINTS:
            deriv = self.calculate_derivatives(data[tp].tolist())
            total += np.array(deriv)
        
        return pd.Series(total, index=data.index)
