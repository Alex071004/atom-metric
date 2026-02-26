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
        
        # Путь к фронтенду
        frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
        frontend_dir = os.path.abspath(frontend_dir)
        
        print(f"   Поиск фронтенда в: {frontend_dir}")
        
        # Копируем файлы, если папка существует
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
            # Создаем простую структуру
            os.makedirs(os.path.join(self.output_dir, "frontend"), exist_ok=True)
        
        return self
            else:
                print(f"   Папка фронтенда не найдена: {frontend_dir}")
            
            # ВАЖНО: Если index.html лежит в frontend, он должен быть в корне output
            if os.path.exists(os.path.join(self.output_dir, "index.html")):
                print("✅ index.html скопирован в корень output")
            else:
                print("❌ index.html не найден!")
            
            return self
    
    def build(self):
        """Полная сборка с гарантированным созданием index.html"""
        print("🏗️ Запуск сборки...")
        
        # Создаем папку output
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📁 Папка output: {os.path.abspath(self.output_dir)}")
        
        # Генерируем JSON данные
        self.build_json_data()
        
        # Копируем файлы из frontend
        self.copy_frontend()
        
        # ГАРАНТИРОВАННО создаем index.html в корне output
        index_path = os.path.join(self.output_dir, "index.html")
        
        # Если index.html еще не существует, создаем его
        if not os.path.exists(index_path):
            print("⚠️ index.html не найден, создаем...")
            
            # Читаем данные для вставки в HTML
            data_path = os.path.join(self.output_dir, "data.json")
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                total_opens = data['summary']['total_opens']
            else:
                total_opens = "N/A"
            
            # Создаем простой, но рабочий index.html
            html_content = f"""<!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>АТОМ Metrics</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ margin: 0; color: #1f77b4; }}
            .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
            .stat-value {{ font-size: 2em; font-weight: bold; color: #1f77b4; }}
            .nav {{ display: flex; gap: 10px; margin-bottom: 20px; }}
            .nav a {{ padding: 10px 20px; background: white; text-decoration: none; color: #333; border-radius: 5px; }}
            .nav a.active {{ background: #1f77b4; color: white; }}
            .info {{ background: #e7f3ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            .chart-container {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🚗 АТОМ Metrics</h1>
                <p>Анализ открытий дверей по тачпоинтам</p>
            </header>
            
            <div class="nav">
                <a href="index.html" class="active">Главная</a>
                <a href="#" onclick="alert('Страница в разработке')">Дашборд</a>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{total_opens}</div>
                    <div>Всего открытий</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="avgDaily">...</div>
                    <div>В среднем в день</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="cars">{config.CARS_COUNT}</div>
                    <div>Машин в парке</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="days">{len(self.df) if hasattr(self, 'df') else '90'}</div>
                    <div>Дней</div>
                </div>
            </div>
            
            <div class="info">
                <p>✅ Сайт успешно собран! Если вы видите эту страницу, значит GitHub Pages работает.</p>
                <p>📊 Данные загружены. Для просмотра графиков подключите frontend/script.js</p>
            </div>
            
            <div class="chart-container">
                <canvas id="simpleChart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <script>
            // Простой скрипт для загрузки данных
            fetch('data.json')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('avgDaily').textContent = data.summary.avg_daily.toFixed(1);
                    
                    // Простой график
                    const ctx = document.getElementById('simpleChart').getContext('2d');
                    new Chart(ctx, {{
                        type: 'line',
                        data: {{
                            labels: data.daily.slice(-10).map(d => d.date),
                            datasets: [{{
                                label: 'Всего открытий',
                                data: data.daily.slice(-10).map(d => d.total),
                                borderColor: '#1f77b4',
                                backgroundColor: 'rgba(31, 119, 180, 0.1)',
                                tension: 0.3
                            }}]
                        }}
                    }});
                }})
                .catch(error => {{
                    console.error('Ошибка загрузки данных:', error);
                    document.getElementById('avgDaily').textContent = 'Ошибка';
                }});
        </script>
        
        <!-- Пытаемся подключить оригинальный скрипт, если он есть -->
        <script src="script.js"></script>
        <script src="frontend/script.js"></script>
    </body>
    </html>"""
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ Создан index.html в {index_path}")
        else:
            print(f"✅ index.html уже существует в {index_path}")
        
        # Показываем содержимое папки
        print("\n📋 Содержимое output:")
        for f in os.listdir(self.output_dir):
            size = os.path.getsize(os.path.join(self.output_dir, f))
            print(f"   - {f} ({size} байт)")
        
        print(f"\n✅ Сборка завершена успешно!")
        return self
if __name__ == "__main__":
    # Для локального тестирования
    builder = StaticSiteBuilder(output_dir="../output")
    builder.generate_data(seed=42).build()
