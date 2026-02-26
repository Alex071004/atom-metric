"""Агрегация метрик в единый отчет."""
import pandas as pd
from typing import Dict, Any
from .derivatives import DerivativeCalculator
from .integrals import IntegralCalculator
import config

class MetricsAggregator:
    """Агрегатор всех метрик."""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.daily_total = IntegralCalculator.daily_total(data)
        self.total_integral = IntegralCalculator.total_all(data)
        self.totals_by_tp = IntegralCalculator.total_by_touchpoint(data)
        
        # Исправление: создаем экземпляр DerivativeCalculator
        self.deriv_calc = DerivativeCalculator(use_smoothing=False, interpolation_points=5)
        self.derivatives = self._calculate_all_derivatives()
        self.angles = self._calculate_all_angles()
        
    def _calculate_all_derivatives(self) -> Dict[str, list]:
        """Производные для всех тачпоинтов."""
        derivs = {}
        for tp in ['button', 'svp', 'va', 'app']:
            # Правильный вызов метода
            _, deriv_values = self.deriv_calc.calculate_derivatives(
                self.data[tp].tolist(), 
                self.data['date'].tolist()
            )
            # Преобразуем в список, если это numpy array
            if hasattr(deriv_values, 'tolist'):
                derivs[tp] = deriv_values.tolist()
            else:
                derivs[tp] = list(deriv_values)
        return derivs
    
    def _calculate_all_angles(self) -> Dict[str, list]:
        """Углы для всех тачпоинтов."""
        angles = {}
        for tp in ['button', 'svp', 'va', 'app']:
            # Используем тот же экземпляр
            angles[tp] = self.deriv_calc.calculate_angles_at_points(
                self.data[tp].tolist(),
                self.data['date'].tolist()
            )
        return angles
    
    def get_summary(self) -> Dict[str, Any]:
        """Получение сводки по метрикам."""
        return {
            'total_opens': self.total_integral,
            'by_touchpoint': self.totals_by_tp,
            'avg_daily': self.daily_total.mean(),
            'max_daily': self.daily_total.max(),
            'min_daily': self.daily_total.min(),
            'avg_derivative': {
                tp: sum(deriv)/len(deriv) if deriv else 0
                for tp, deriv in self.derivatives.items()
            }
        }