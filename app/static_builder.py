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
    
    def __init__(self, output_dir="output"):
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
        
        summary = self.metrics.get_summary()
        
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
        
        calc = DerivativeCalculator(use_smoothing=True, interpolation_points=10)
        derivatives = {}
        for tp in config.TOUCHPOINTS:
            _, tangents = calc.calculate_derivatives(
                self.df[tp].tolist(), 
                self.df['date'].tolist()
            )
            derivatives[tp] = [float(x) for x in tangents]
        
        output = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_opens': int(summary['total_opens']),
                'avg_daily': float(summary['avg_daily']),
                'max_daily': float(summary['max_daily']),
                'min_daily': float(summary['min_daily']),
                'days': int(len(self.df)),
                'cars': int(config.CARS_COUNT)
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
        
        os.makedirs(self.output_dir, exist_ok=True)
        with open(f"{self.output_dir}/data.json", 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        return self
    
    def copy_frontend(self):
        """Копирование фронтенда в output."""
        print("📁 Копирование фронтенда...")
        
        frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
        frontend_dir = os.path.abspath(frontend_dir)
        
        print(f"   Поиск фронтенда в: {frontend_dir}")
        
        if os.path.exists(frontend_dir):
            files_copied = 0
            for file in os.listdir(frontend_dir):
                src = os.path.join(frontend_dir, file)
                dst = os.path.join(self.output_dir, file)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    files_copied += 1
                    print(f"   ✅ Скопирован: {file}")
            
            if files_copied == 0:
                print("   ⚠️ В папке frontend нет файлов для копирования")
        else:
            print(f"   ⚠️ Папка фронтенда не найдена: {frontend_dir}")
            os.makedirs(os.path.join(self.output_dir, "frontend"), exist_ok=True)
        
        return self
    
    def build(self):
        """Полная сборка с гарантированным созданием index.html"""
        print("🏗️ Запуск сборки...")
        
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📁 Папка output: {os.path.abspath(self.output_dir)}")
        
        self.build_json_data()
        self.copy_frontend()
        
        index_path = os.path.join(self.output_dir, "index.html")
        
        if not os.path.exists(index_path):
            print("⚠️ index.html не найден, создаем упрощенную версию...")
            
            data_path = os.path.join(self.output_dir, "data.json")
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                total_opens = data['summary']['total_opens']
            else:
                total_opens = "N/A"
            
            # Исправленный HTML с правильными путями и без дублирования графиков
            html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>АТОМ Metrics</title>
    <!-- ПРАВИЛЬНЫЙ ПУТЬ к CSS -->
    <link rel="stylesheet" href="frontend/styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="app">
        <header>
            <h1>🚗 АТОМ Metrics</h1>
            <p>Анализ открытий дверей по тачпоинтам</p>
        </header>
        
        <nav>
            <a href="index.html" class="active">Главная</a>
            <a href="frontend/dashboard.html">Дашборд</a>
        </nav>
        
        <div class="stats-cards" id="statsCards">
            <div class="stat-card">
                <div class="stat-value">{total_opens}</div>
                <div class="stat-label">Всего открытий</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avgDaily">...</div>
                <div class="stat-label">В среднем в день</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="cars">{config.CARS_COUNT}</div>
                <div class="stat-label">Машин в парке</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="days">{len(self.df)}</div>
                <div class="stat-label">Дней</div>
            </div>
        </div>
        
        <!-- Контейнеры для графиков будут заполнены из frontend/script.js -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3>Все тачпоинты</h3>
                <canvas id="allTouchpointsChart"></canvas>
            </div>
            <div class="chart-card">
                <h3>Распределение</h3>
                <canvas id="pieChart"></canvas>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h3>Суммарные открытия</h3>
                <canvas id="totalChart"></canvas>
            </div>
            <div class="chart-card">
                <h3>Производные</h3>
                <canvas id="derivativesChart"></canvas>
            </div>
        </div>
    </div>
    
    <!-- ПРАВИЛЬНЫЕ ПУТИ к скриптам. ВАЖНО: сначала data, потом script -->
    <script src="data.json" id="data-json"></script>
    <script src="frontend/script.js"></script>
</body>
</html>'''
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ Создан index.html в {index_path}")
        else:
            print(f"✅ index.html уже существует в {index_path}")
        
        print("\n📋 Содержимое output:")
        for f in os.listdir(self.output_dir):
            size = os.path.getsize(os.path.join(self.output_dir, f))
            print(f"   - {f} ({size} байт)")
        
        print("\n✅ Сборка завершена успешно!")
        return self

if __name__ == "__main__":
    builder = StaticSiteBuilder(output_dir="output")
    builder.generate_data(seed=42).build()
