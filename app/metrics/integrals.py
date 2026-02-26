"""Вычисление интегралов (сумм) для дискретных данных."""
import pandas as pd
from typing import Dict
import config

class IntegralCalculator:
    """
    Калькулятор интегралов для дискретных функций.
    Интеграл = сумма значений по дням (дискретный аналог)
    """
    
    @staticmethod
    def total_by_touchpoint(data: pd.DataFrame) -> Dict[str, int]:
        """
        Общее число открытий за весь период по каждому тачпоинту.
        """
        totals = {}
        for tp in config.TOUCHPOINTS:
            totals[tp] = data[tp].sum()
        return totals
    
    @staticmethod
    def total_all(data: pd.DataFrame) -> int:
        """
        Общее число открытий за весь период (интеграл).
        """
        return data[config.TOUCHPOINTS].sum().sum()
    
    @staticmethod
    def daily_total(data: pd.DataFrame) -> pd.Series:
        """
        Сумма открытий по дням (все тачпоинты вместе).
        """
        return data[config.TOUCHPOINTS].sum(axis=1)