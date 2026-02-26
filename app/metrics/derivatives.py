"""Вычисление производных и углов наклона."""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy import interpolate
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from .approximation import DataApproximator

class DerivativeCalculator:
    """
    Калькулятор производных для дискретных функций.
    Возвращает тангенс угла наклона (Δy/Δx), а не градусы.
    """
    
    def __init__(self, use_smoothing: bool = True, interpolation_points: int = 10):
        self.use_smoothing = use_smoothing
        # Для сглаживания используем адаптивный параметр
        self.approximator = DataApproximator(smoothing_factor=None, 
                                            interpolation_points=interpolation_points)
    
    def calculate_derivatives(self, values: List[int], dates: Optional[List] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Вычисление производных (тангенса угла наклона).
        Возвращает (x, tangent_values)
        """
        if dates is None:
            x = np.arange(len(values))
        else:
            x = np.arange(len(dates))
        
        if self.use_smoothing:
            return self.approximator.calculate_smoothed_derivative(x, values, per_car=True)
        else:
            return self.approximator.calculate_derivative_tangent(x, values, per_car=True)
    
    def calculate_angles_at_points(self, values: List[int], dates: Optional[List] = None) -> List[float]:
        """
        Вычисление тангенсов только в исходных точках.
        """
        x = np.arange(len(values))
        
        if self.use_smoothing:
            x_dense, tangents_dense = self.approximator.calculate_smoothed_derivative(x, values, per_car=True)
            # Интерполируем обратно в исходные точки
            f = interpolate.interp1d(x_dense, tangents_dense, kind='linear', 
                                    bounds_error=False, fill_value='extrapolate')
            tangents = f(x)
            return tangents.tolist()
        else:
            _, tangents = self.approximator.calculate_derivative_tangent(x, values, per_car=True)
            return tangents.tolist()
    
    def sum_of_angles(self, data: pd.DataFrame) -> pd.Series:
        """
        Сумма тангенсов углов наклона всех тачпоинтов.
        """
        x = np.arange(len(data))
        total_tangents = np.zeros(len(x))
        
        for tp in config.TOUCHPOINTS:
            _, tangents = self.calculate_derivatives(data[tp].tolist(), data['date'].tolist())
            # Интерполируем обратно в исходные точки
            f = interpolate.interp1d(np.arange(len(tangents)), tangents, kind='linear',
                                    bounds_error=False, fill_value='extrapolate')
            tangents_at_x = f(x)
            total_tangents += tangents_at_x
        
        return pd.Series(total_tangents, index=data.index)