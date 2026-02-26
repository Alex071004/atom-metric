"""Генерация данных с трендами по тачпоинтам."""
import numpy as np
from datetime import timedelta
from typing import List
import config
from .schema import TouchpointData

class DataGenerator:
    """Генератор данных с реалистичными трендами для 100 машин."""
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        
    def generate(self) -> TouchpointData:
        """Генерация данных за config.DAYS дней."""
        dates = [config.START_DATE + timedelta(days=i) for i in range(config.DAYS)]
        
        # Параметры трендов (доли)
        # Кнопка: экспоненциальное убывание от 0.8 до 0.6
        p_button0 = 0.8
        p_button_plateau = 0.6
        lambda_button = 0.05
        
        # СВП: распределение Вейбулла с пиком ~0.15 на 30-й день
        weibull_scale = 42.0      # масштаб (пик при t=30)
        weibull_shape = 2.0
        base_svp = 0.1
        A_svp = 2.45               # амплитуда для достижения пика 0.15
        
        # VA: экспоненциальный рост от 0.05 до ~0.22
        p_va0 = 0.05
        p_va_plateau = 0.2183      # целевое значение на плато (из расчёта)
        lambda_va = 0.05
        
        # Приложение: стабильно около 5%
        p_app_base = 0.05
        
        # Массивы долей по дням
        p_button = np.zeros(config.DAYS)
        p_svp = np.zeros(config.DAYS)
        p_va = np.zeros(config.DAYS)
        p_app = np.zeros(config.DAYS)
        
        for t in range(config.DAYS):
            if t < config.TREND_DAYS:  # первые 60 дней
                # Кнопка
                p_button[t] = p_button_plateau + (p_button0 - p_button_plateau) * np.exp(-lambda_button * t)
                
                # СВП (Вейбулл)
                x = t / weibull_scale
                f_weibull = (weibull_shape / weibull_scale) * (x ** (weibull_shape - 1)) * np.exp(-(x ** weibull_shape))
                p_svp[t] = base_svp + A_svp * f_weibull
                
                # VA (экспоненциальный рост)
                p_va[t] = p_va_plateau - (p_va_plateau - p_va0) * np.exp(-lambda_va * t)
                
                # Приложение (константа)
                p_app[t] = p_app_base
            else:
                # Плато: значения последнего дня тренда (индекс TREND_DAYS-1)
                p_button[t] = p_button[config.TREND_DAYS - 1]
                p_svp[t] = p_svp[config.TREND_DAYS - 1]
                p_va[t] = p_va[config.TREND_DAYS - 1]
                p_app[t] = p_app_base
        
        # Нормировка долей, чтобы сумма была точно 1
        total_p = p_button + p_svp + p_va + p_app
        p_button /= total_p
        p_svp /= total_p
        p_va /= total_p
        p_app /= total_p
        
        # Генерация целых чисел открытий
        button_counts = []
        svp_counts = []
        va_counts = []
        app_counts = []
        
        for t in range(config.DAYS):
            # Общее число открытий в день (Пуассон со средним TOTAL_AVG_OPENINGS)
            N = self.rng.poisson(config.TOTAL_AVG_OPENINGS)
            # Мультиномиальное распределение по тачпоинтам
            probs = [p_button[t], p_svp[t], p_va[t], p_app[t]]
            counts = self.rng.multinomial(N, probs)
            button_counts.append(int(counts[0]))
            svp_counts.append(int(counts[1]))
            va_counts.append(int(counts[2]))
            app_counts.append(int(counts[3]))
        
        return TouchpointData(
            dates=dates,
            button=button_counts,
            svp=svp_counts,
            va=va_counts,
            app=app_counts
        )