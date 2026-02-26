"""Аппроксимация и сглаживание дискретных данных."""
import numpy as np
from scipy import interpolate
from typing import Tuple, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class DataApproximator:
    """Класс для аппроксимации дискретных данных."""
    
    def __init__(self, smoothing_factor: float = None, interpolation_points: int = 10):
        """
        smoothing_factor: параметр сглаживания (0-1, где 1 = максимально гладко)
        interpolation_points: количество точек между исходными днями
        """
        self.smoothing_factor = smoothing_factor
        self.interpolation_points = interpolation_points
    
    def smooth_curve(self, x: List[float], y: List[float]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Сглаживание кривой с адаптивным параметром сглаживания.
        Кривая НЕ проходит через исходные точки.
        """
        if len(x) < 4:
            return np.array(x), np.array(y)
        
        x = np.array(x)
        y = np.array(y)
        
        # Нормализуем x для лучшей численной стабильности
        x_min, x_max = x.min(), x.max()
        if x_max - x_min < 1e-10:
            x_norm = np.zeros_like(x)
        else:
            x_norm = (x - x_min) / (x_max - x_min)
        
        # Адаптивный параметр сглаживания на основе разброса данных
        if self.smoothing_factor is None:
            # Вычисляем относительный разброс данных
            y_range = np.ptp(y)  # размах (max - min)
            y_std = np.std(y)     # стандартное отклонение
            
            if y_range < 1e-10:
                # Практически константа - максимальное сглаживание
                s_factor = 0.9
            else:
                # Нормализованный разброс относительно среднего
                y_mean = np.mean(y)
                if abs(y_mean) > 1e-10:
                    relative_spread = y_std / abs(y_mean)
                else:
                    relative_spread = y_std
                
                # Для СВП и Приложения relative_spread может быть большим
                # Чем больше разброс, тем больше сглаживание
                if relative_spread > 0.5:
                    s_factor = 0.8  # сильное сглаживание
                elif relative_spread > 0.3:
                    s_factor = 0.6  # среднее сглаживание
                else:
                    s_factor = 0.4  # слабое сглаживание
        else:
            s_factor = self.smoothing_factor
        
        # Параметр сглаживания для splrep
        # s = s_factor * len(x) * np.var(y)
        # Увеличиваем s для более сильного сглаживания
        s = s_factor * len(x) * np.var(y) * 2.0  # Удваиваем для гарантии
        
        try:
            # Пробуем разные степени сглаживания
            for k in [3, 2]:  # сначала кубический, потом квадратичный
                try:
                    tck = interpolate.splrep(x_norm, y, s=s, k=k)
                    break
                except:
                    continue
            
            # Создаем плотную сетку
            x_dense_norm = np.linspace(0, 1, len(x) * self.interpolation_points)
            y_dense = interpolate.splev(x_dense_norm, tck)
            
            # Дополнительное сглаживание скользящим средним для очень шумных данных
            if s_factor > 0.6:
                window = max(3, len(y_dense) // 50)
                if window % 2 == 0:
                    window += 1
                if window > 1:
                    from scipy.ndimage import uniform_filter1d
                    y_dense = uniform_filter1d(y_dense, size=window, mode='nearest')
            
            # Возвращаем x в исходный масштаб
            x_dense = x_min + x_dense_norm * (x_max - x_min)
            
            return x_dense, y_dense
            
        except Exception as e:
            print(f"Ошибка сглаживания: {e}, используем полиномиальную регрессию")
            # Fallback на полиномиальную регрессию
            try:
                # Полином 3-й степени
                coeffs = np.polyfit(x_norm, y, 3)
                poly = np.poly1d(coeffs)
                x_dense_norm = np.linspace(0, 1, len(x) * self.interpolation_points)
                y_dense = poly(x_dense_norm)
                x_dense = x_min + x_dense_norm * (x_max - x_min)
                return x_dense, y_dense
            except:
                # Если совсем плохо - линейная интерполяция со сглаживанием
                f = interpolate.interp1d(x, y, kind='linear', fill_value='extrapolate')
                x_dense = np.linspace(x_min, x_max, len(x) * self.interpolation_points)
                y_dense = f(x_dense)
                # Применяем скользящее среднее
                window = max(3, len(y_dense) // 30)
                if window % 2 == 0:
                    window += 1
                from scipy.ndimage import uniform_filter1d
                y_dense = uniform_filter1d(y_dense, size=window, mode='nearest')
                return x_dense, y_dense
    
    def calculate_derivative_tangent(self, x: List[float], y: List[float], per_car: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Вычисление производной (тангенса угла наклона) методом трапеций.
        """
        x = np.array(x)
        y = np.array(y)
        
        if per_car:
            y = y / config.CARS_COUNT
        
        # Производная центральными разностями
        derivative = np.zeros_like(y, dtype=float)
        
        if len(x) > 1:
            derivative[0] = (y[1] - y[0]) / (x[1] - x[0])
            derivative[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])
            
            for i in range(1, len(x)-1):
                h_left = x[i] - x[i-1]
                h_right = x[i+1] - x[i]
                # Центральная разность с неравномерным шагом
                derivative[i] = (y[i+1] - y[i-1]) / (h_left + h_right)
        
        return x, derivative
    
    def calculate_smoothed_derivative(self, x: List[float], y: List[float], per_car: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Вычисление производной на сглаженной кривой.
        """
        # Сглаживаем кривую с адаптивным параметром
        x_dense, y_dense = self.smooth_curve(x, y)
        
        if per_car:
            y_dense = y_dense / config.CARS_COUNT
        
        # Производная на плотной сетке
        derivative = np.gradient(y_dense, x_dense)
        
        # Дополнительное сглаживание производной
        if len(derivative) > 10:
            window = max(3, len(derivative) // 40)
            if window % 2 == 0:
                window += 1
            from scipy.ndimage import uniform_filter1d
            derivative = uniform_filter1d(derivative, size=window, mode='nearest')
        
        return x_dense, derivative