"""Генератор статических HTML/JSON файлов для GitHub Pages."""
import json
import os
import shutil
from datetime import datetime
import numpy as np

from app.data.generator import DataGenerator
from app.metrics.aggregator import MetricsAggregator
from app.metrics.derivatives import DerivativeCalculator
from app.metrics.integrals import IntegralCalculator
import config

class StaticSiteBuilder:
    """Сборщик статического сайта."""
    
    def __init__(self, output_dir="../output"):
        self.output_dir = output_dir
        self.data = None
        self.df = None
        self.metrics = None
        
    def generate_data(self, seed=42):
        """Генерация данных."""
        print("📊 Генерация данных...")
        generator = DataGenerator(seed=seed)
        self.data = generator.generate()
        self.df = self.data.to_dataframe()
        self.metrics = MetricsAggregator(self.df)
        return self
    
    def build_json_data(self):
        """Экспорт всех данных в JSON."""
        print("💾 Экспорт JSON...")
        
        # Основная статистика
        summary = self.metrics.get_summary()
        
        # Данные по дням
        daily_data = []
        for idx, row in self.df.iterrows():
            daily_data.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'button': int(row['button']),  # явное преобразование в int
                'svp': int(row['svp']),
                'va': int(row['va']),
                'app': int(row['app']),
                'total': int(row['button'] + row['svp'] + row['va'] + row['app'])
            })
        
        # Производные
        calc = DerivativeCalculator(use_smoothing=True, interpolation_points=10)
        derivatives = {}
        for tp in config.TOUCHPOINTS:
            _, tangents = calc.calculate_derivatives(
                self.df[tp].tolist(), 
                self.df['date'].tolist()
            )
            # Преобразуем numpy array в список Python-чисел
            derivatives[tp] = [float(x) for x in tangents]  # важно: float()
        
        # Итоговый JSON с явным преобразованием всех numpy типов
        output = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_opens': int(summary['total_opens']),  # int()
                'avg_daily': float(summary['avg_daily']),    # float()
                'max_daily': float(summary['max_daily']),
                'min_daily': float(summary['min_daily']),
                'days': int(len(self.df)),
                'cars': int(config.CARS_COUNT)
            },
            'by_touchpoint': {
                tp: {
                    'total': int(summary['by_touchpoint'][tp]),  # int()
                    'percentage': float(summary['by_touchpoint'][tp] / summary['total_opens'] * 100),  # float()
                    'name': config.TOUCHPOINT_NAMES_RU[tp]
                }
                for tp in config.TOUCHPOINTS
            },
            'daily': daily_data,
            'derivatives': derivatives
        }
        
        # Сохраняем
        os.makedirs(self.output_dir, exist_ok=True)
        with open(f"{self.output_dir}/data.json", 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        return self
    
    def copy_frontend(self):
        """Копирование фронтенда в output."""
        print("📁 Копирование фронтенда...")
        
        # Создаем output если нет
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Путь к фронтенду
        frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
        frontend_dir = os.path.abspath(frontend_dir)
        
        print(f"   Копируем из: {frontend_dir}")
        
        # Копируем все файлы из frontend в output
        if os.path.exists(frontend_dir):
            for file in os.listdir(frontend_dir):
                src = os.path.join(frontend_dir, file)
                dst = os.path.join(self.output_dir, file)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    print(f"   Скопирован: {file}")
        else:
            print(f"   Папка фронтенда не найдена: {frontend_dir}")
        
        # ВАЖНО: Если index.html лежит в frontend, он должен быть в корне output
        if os.path.exists(os.path.join(self.output_dir, "index.html")):
            print("✅ index.html скопирован в корень output")
        else:
            print("❌ index.html не найден!")
        
        return self
    
    def build(self):
        """Полная сборка."""
        self.build_json_data()
        self.copy_frontend()
        print(f"✅ Сайт собран в {self.output_dir}/")
        return self

if __name__ == "__main__":
    # Для локального тестирования
    builder = StaticSiteBuilder(output_dir="../output")
    builder.generate_data(seed=42).build()
