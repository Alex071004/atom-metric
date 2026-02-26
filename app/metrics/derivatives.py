"""Упрощенное вычисление производных с увеличенным шагом."""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class DerivativeCalculator:
    """Калькулятор производных с настраиваемым шагом."""
    
    def __init__(self, step: int = 5):
        """
        step: шаг дифференцирования (количество дней между точками)
        Чем больше шаг, тем сильнее сглаживание и лучше виден тренд
        """
        self.step = step
    
    def calculate_derivatives(self, values: List[int]) -> List[float]:
        """
        Вычисление производных с заданным шагом.
        Результат на одну машину.
        """
        y = np.array(values) / config.CARS_COUNT
        x = np.arange(len(y))
        
        # Производная через разность с шагом step
        derivatives = np.zeros_like(y)
        
        if len(y) > self.step:
            # Для внутренних точек используем центральную разность с шагом step
            for i in range(self.step, len(y) - self.step):
                derivatives[i] = (y[i + self.step] - y[i - self.step]) / (x[i + self.step] - x[i - self.step])
            
            # Для начала ряда (первые step точек) - используем возрастающий шаг
            for i in range(1, self.step):
                if i + self.step < len(y):
                    derivatives[i] = (y[i + self.step] - y[0]) / (x[i + self.step] - x[0])
            
            # Для конца ряда (последние step точек) - используем убывающий шаг
            for i in range(len(y) - self.step, len(y)):
                if i - self.step >= 0:
                    derivatives[i] = (y[-1] - y[i - self.step]) / (x[-1] - x[i - self.step])
            
            # Самая первая и самая последняя точки - экстраполяция
            if self.step < len(y):
                derivatives[0] = derivatives[self.step]
                derivatives[-1] = derivatives[-self.step - 1]
        else:
            # Если данных мало, используем обычный метод
            if len(y) >= 2:
                derivatives[0] = (y[1] - y[0]) / (x[1] - x[0])
                derivatives[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])
            
            for i in range(1, len(y)-1):
                derivatives[i] = (y[i+1] - y[i-1]) / (x[i+1] - x[i-1])
        
        return derivatives.tolist()
    
    def sum_of_derivatives(self, data: pd.DataFrame) -> pd.Series:
        """Сумма производных всех тачпоинтов."""
        total = np.zeros(len(data))
        
        for tp in config.TOUCHPOINTS:
            deriv = self.calculate_derivatives(data[tp].tolist())
            total += np.array(deriv)
        
        return pd.Series(total, index=data.index)
