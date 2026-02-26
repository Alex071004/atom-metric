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
                'button': int(row['button']),
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
            derivatives[tp] = tangents.tolist()
        
        # Итоговый JSON
        output = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_opens': summary['total_opens'],
                'avg_daily': float(summary['avg_daily']),
                'max_daily': float(summary['max_daily']),
                'min_daily': float(summary['min_daily']),
                'days': len(self.df),
                'cars': config.CARS_COUNT
            },
            'by_touchpoint': {
                tp: {
                    'total': int(summary['by_touchpoint'][tp]),
                    'percentage': float(summary['by_touchpoint'][tp] / summary['total_opens'] * 100),
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
        
        # Копируем все HTML/CSS/JS
        frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
        for file in os.listdir(frontend_dir):
            if file.endswith(('.html', '.css', '.js')):
                shutil.copy2(
                    os.path.join(frontend_dir, file),
                    os.path.join(self.output_dir, file)
                )
        
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
