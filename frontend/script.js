// Глобальные переменные для хранения графиков
let chartInstances = {};

// Функция загрузки данных
async function loadData() {
    try {
        console.log('Загрузка данных...');
        
        // Показываем индикатор загрузки
        document.getElementById('loading').style.display = 'block';
        
        // Загружаем данные (data.json в той же папке)
        const response = await fetch('data.json');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Данные загружены:', data);
        
        // Скрываем индикатор загрузки
        document.getElementById('loading').style.display = 'none';
        
        // Показываем контейнеры
        document.getElementById('statsCards').style.display = 'grid';
        document.getElementById('chartsGrid').style.display = 'grid';
        document.getElementById('dataTable').style.display = 'block';
        
        // Обновляем все компоненты
        updateStatsCards(data);
        createAllCharts(data);
        updateTable(data);
        
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
        document.getElementById('error').innerHTML = 'Ошибка загрузки данных: ' + error.message;
    }
}

// Обновление статистики
function updateStatsCards(data) {
    const statsCards = document.getElementById('statsCards');
    
    // Очищаем существующие карточки
    statsCards.innerHTML = '';
    
    // Создаем карточки
    const cards = [
        { label: 'Всего открытий', value: data.summary.total_opens.toLocaleString() },
        { label: 'В среднем в день', value: data.summary.avg_daily.toFixed(1) },
        { label: 'Машин в парке', value: data.summary.cars },
        { label: 'Дней анализа', value: data.summary.days }
    ];
    
    cards.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'stat-card';
        cardElement.innerHTML = `
            <div class="stat-value">${card.value}</div>
            <div class="stat-label">${card.label}</div>
        `;
        statsCards.appendChild(cardElement);
    });
}

// Создание всех графиков
function createAllCharts(data) {
    // Уничтожаем старые графики если есть
    Object.values(chartInstances).forEach(chart => {
        if (chart) chart.destroy();
    });
    
    // Подготовка данных
    const dates = data.daily.map(d => {
        const date = new Date(d.date);
        return `${date.getDate()}.${date.getMonth() + 1}`;
    });
    
    // 1. График всех тачпоинтов
    const allCtx = document.getElementById('allTouchpointsChart').getContext('2d');
    chartInstances.all = new Chart(allCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Кнопка',
                    data: data.daily.map(d => d.button),
                    borderColor: '#1f77b4',
                    backgroundColor: 'rgba(31, 119, 180, 0.1)',
                    tension: 0.3,
                    pointRadius: 2
                },
                {
                    label: 'СВП',
                    data: data.daily.map(d => d.svp),
                    borderColor: '#ff7f0e',
                    backgroundColor: 'rgba(255, 127, 14, 0.1)',
                    tension: 0.3,
                    pointRadius: 2
                },
                {
                    label: 'VA',
                    data: data.daily.map(d => d.va),
                    borderColor: '#2ca02c',
                    backgroundColor: 'rgba(44, 160, 44, 0.1)',
                    tension: 0.3,
                    pointRadius: 2
                },
                {
                    label: 'Приложение',
                    data: data.daily.map(d => d.app),
                    borderColor: '#d62728',
                    backgroundColor: 'rgba(214, 39, 40, 0.1)',
                    tension: 0.3,
                    pointRadius: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // 2. Круговая диаграмма
    const pieCtx = document.getElementById('pieChart').getContext('2d');
    chartInstances.pie = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: ['Кнопка', 'СВП', 'VA', 'Приложение'],
            datasets: [{
                data: [
                    data.by_touchpoint.button.total,
                    data.by_touchpoint.svp.total,
                    data.by_touchpoint.va.total,
                    data.by_touchpoint.app.total
                ],
                backgroundColor: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // 3. Суммарные открытия
    const totalCtx = document.getElementById('totalChart').getContext('2d');
    chartInstances.total = new Chart(totalCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Всего открытий',
                data: data.daily.map(d => d.total),
                borderColor: '#9467bd',
                backgroundColor: 'rgba(148, 103, 189, 0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    // 4. Производные (только для Кнопки и СВП для наглядности)
    const derivCtx = document.getElementById('derivativesChart').getContext('2d');
    
    // Берем производные (они уже на 1 машину)
    const buttonDeriv = data.derivatives.button.slice(0, dates.length);
    const svpDeriv = data.derivatives.svp.slice(0, dates.length);
    
    chartInstances.derivatives = new Chart(derivCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Кнопка (производная)',
                    data: buttonDeriv,
                    borderColor: '#1f77b4',
                    borderDash: [5, 5],
                    tension: 0.3,
                    pointRadius: 1
                },
                {
                    label: 'СВП (производная)',
                    data: svpDeriv,
                    borderColor: '#ff7f0e',
                    borderDash: [5, 5],
                    tension: 0.3,
                    pointRadius: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Тангенс угла наклона'
                    }
                }
            }
        }
    });
}

// Обновление таблицы
function updateTable(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    
    // Берем последние 10 дней
    const last10Days = data.daily.slice(-10).reverse();
    
    last10Days.forEach(day => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${day.date}</td>
            <td>${day.button}</td>
            <td>${day.svp}</td>
            <td>${day.va}</td>
            <td>${day.app}</td>
            <td><strong>${day.total}</strong></td>
        `;
        tbody.appendChild(row);
    });
}

// Обработка изменения размера окна
window.addEventListener('resize', () => {
    // Перерисовываем графики при изменении размера
    Object.values(chartInstances).forEach(chart => {
        if (chart) chart.resize();
    });
});

// Запуск загрузки данных при загрузке страницы
document.addEventListener('DOMContentLoaded', loadData);
