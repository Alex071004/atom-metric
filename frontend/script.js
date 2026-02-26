// Глобальные переменные для хранения графиков
let chartInstances = {};

// Функция загрузки данных
async function loadData() {
    try {
        document.getElementById('loading').style.display = 'block';
        
        const response = await fetch('data.json');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        console.log('Данные загружены:', data);
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('statsCards').style.display = 'grid';
        document.getElementById('chartsGrid').style.display = 'grid';
        document.getElementById('dataTable').style.display = 'block';
        
        updateStatsCards(data);
        createAllCharts(data);
        updateTable(data);
        
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
    }
}

// Обновление статистики
function updateStatsCards(data) {
    const statsCards = document.getElementById('statsCards');
    statsCards.innerHTML = '';
    
    const cards = [
        { label: 'Всего открытий', value: data.summary.total_opens.toLocaleString() },
        { label: 'Среднее в день', value: data.summary.avg_daily.toFixed(1) },
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

// Функция для создания вертикальных линий
function createAnnotations(daysCount) {
    const annotations = {};
    
    for (let i = 30; i <= daysCount; i += 30) {
        annotations[`line${i}`] = {
            type: 'line',
            xMin: i,
            xMax: i,
            borderColor: 'rgba(0, 0, 0, 0.2)',
            borderWidth: 1,
            borderDash: [5, 5],
            label: {
                display: true,
                content: `${i} день`,
                position: 'start',
                backgroundColor: 'rgba(0, 0, 0, 0.05)',
                font: { size: 10 }
            }
        };
    }
    
    return annotations;
}

// Создание всех графиков
function createAllCharts(data) {
    // Уничтожаем старые графики
    Object.values(chartInstances).forEach(chart => {
        if (chart) chart.destroy();
    });
    
    const daysCount = data.daily.length;
    const daysFromStart = data.daily.map((_, index) => index + 1);
    const annotations = createAnnotations(daysCount);

    // 1. График всех тачпоинтов
    const allCtx = document.getElementById('allTouchpointsChart').getContext('2d');
    chartInstances.all = new Chart(allCtx, {
        type: 'line',
        data: {
            labels: daysFromStart,
            datasets: [
                {
                    label: 'Кнопка',
                    data: data.daily.map(d => d.button),
                    borderColor: '#1f77b4',
                    backgroundColor: 'rgba(31, 119, 180, 0.1)',
                    tension: 0.3,
                    pointRadius: 1,
                    borderWidth: 2
                },
                {
                    label: 'СВП',
                    data: data.daily.map(d => d.svp),
                    borderColor: '#ff7f0e',
                    backgroundColor: 'rgba(255, 127, 14, 0.1)',
                    tension: 0.3,
                    pointRadius: 1,
                    borderWidth: 2
                },
                {
                    label: 'VA',
                    data: data.daily.map(d => d.va),
                    borderColor: '#2ca02c',
                    backgroundColor: 'rgba(44, 160, 44, 0.1)',
                    tension: 0.3,
                    pointRadius: 1,
                    borderWidth: 2
                },
                {
                    label: 'Приложение',
                    data: data.daily.map(d => d.app),
                    borderColor: '#d62728',
                    backgroundColor: 'rgba(214, 39, 40, 0.1)',
                    tension: 0.3,
                    pointRadius: 1,
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                annotation: { annotations: annotations }
            },
            scales: {
                x: { 
                    title: { display: true, text: 'День с начала релиза' },
                    min: 1,
                    max: daysCount
                },
                y: { 
                    beginAtZero: true,
                    title: { display: true, text: 'Количество открытий' }
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
            plugins: { legend: { position: 'bottom' } }
        }
    });
    
    // 3. Суммарные открытия
    const totalData = data.daily.map(d => d.total);
    const avgTotal = totalData.reduce((a, b) => a + b, 0) / totalData.length;
    
    const totalCtx = document.getElementById('totalChart').getContext('2d');
    chartInstances.total = new Chart(totalCtx, {
        type: 'line',
        data: {
            labels: daysFromStart,
            datasets: [
                {
                    label: 'Всего открытий',
                    data: totalData,
                    borderColor: '#9467bd',
                    backgroundColor: 'rgba(148, 103, 189, 0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 1,
                    borderWidth: 2
                },
                {
                    label: `Среднее (${avgTotal.toFixed(1)})`,
                    data: Array(daysFromStart.length).fill(avgTotal),
                    borderColor: '#ff0000',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                annotation: { annotations: annotations }
            },
            scales: {
                x: { 
                    title: { display: true, text: 'День с начала релиза' },
                    min: 1,
                    max: daysCount
                },
                y: { 
                    beginAtZero: true,
                    title: { display: true, text: 'Количество открытий' }
                }
            }
        }
    });
    
    // 4. Производные - ИСПРАВЛЕНО
    const derivCtx = document.getElementById('derivativesChart').getContext('2d');
    
    // Находим максимальное абсолютное значение для масштабирования
    const allDerivValues = [
        ...data.derivatives.button,
        ...data.derivatives.svp,
        ...data.derivatives.va,
        ...data.derivatives.app
    ].filter(v => !isNaN(v) && isFinite(v));
    
    const maxAbsDeriv = Math.max(...allDerivValues.map(Math.abs)) * 1.2;
    
    chartInstances.derivatives = new Chart(derivCtx, {
        type: 'line',
        data: {
            labels: daysFromStart,  // те же дни, что и для основных данных
            datasets: [
                {
                    label: 'Кнопка',
                    data: data.derivatives.button,
                    borderColor: '#1f77b4',
                    tension: 0.1,
                    pointRadius: 0.5,
                    borderWidth: 2
                },
                {
                    label: 'СВП',
                    data: data.derivatives.svp,
                    borderColor: '#ff7f0e',
                    tension: 0.1,
                    pointRadius: 0.5,
                    borderWidth: 2
                },
                {
                    label: 'VA',
                    data: data.derivatives.va,
                    borderColor: '#2ca02c',
                    tension: 0.1,
                    pointRadius: 0.5,
                    borderWidth: 2
                },
                {
                    label: 'Приложение',
                    data: data.derivatives.app,
                    borderColor: '#d62728',
                    tension: 0.1,
                    pointRadius: 0.5,
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                annotation: { annotations: annotations }
            },
            scales: {
                x: { 
                    title: { display: true, text: 'День с начала релиза' },
                    min: 1,
                    max: daysCount
                },
                y: { 
                    title: { display: true, text: 'Производная' },
                    min: -maxAbsDeriv,
                    max: maxAbsDeriv,
                    grid: {
                        color: context => context.tick.value === 0 ? '#000000' : '#e0e0e0',
                        lineWidth: context => context.tick.value === 0 ? 2 : 1
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

// Обработка ресайза
window.addEventListener('resize', () => {
    Object.values(chartInstances).forEach(chart => {
        if (chart) chart.resize();
    });
});

// Запуск
document.addEventListener('DOMContentLoaded', loadData);
