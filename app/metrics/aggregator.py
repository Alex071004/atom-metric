"""Агрегация метрик в единый отчет."""
import pandas as pd
from typing import Dict, Any
from .derivatives import DerivativeCalculator
from .integrals import IntegralCalculator
import config

class MetricsAggregator:
    """Агрегатор всех метрик."""
    
    def __init__(self, data: pd.DataFrame, deriv_step: int = 5):
        """
        deriv_step: шаг для вычисления производных (по умолчанию 5 дней)
        """
        self.data = data
        self.daily_total = IntegralCalculator.daily_total(data)
        self.total_integral = IntegralCalculator.total_all(data)
        self.totals_by_tp = IntegralCalculator.total_by_touchpoint(data)
        
        # Используем увеличенный шаг для сглаживания
        self.deriv_calc = DerivativeCalculator(step=deriv_step)
        self.derivatives = self._calculate_all_derivatives()
        
    def _calculate_all_derivatives(self) -> Dict[str, list]:
        """Производные для всех тачпоинтов."""
        derivs = {}
        for tp in ['button', 'svp', 'va', 'app']:
            deriv_values = self.deriv_calc.calculate_derivatives(
                self.data[tp].tolist()
            )
            derivs[tp] = deriv_values
        return derivs
    
    def get_summary(self) -> Dict[str, Any]:
        """Получение сводки по метрикам."""
        return {
            'total_opens': self.total_integral,
            'by_touchpoint': self.totals_by_tp,
            'avg_daily': self.daily_total.mean(),
            'max_daily': self.daily_total.max(),
            'min_daily': self.daily_total.min()
        }
