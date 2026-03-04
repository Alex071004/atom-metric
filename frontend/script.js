// frontend/script.js
// Глобальные переменные для хранения графиков
window.chartInstances = {};

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

// Функция обновления статистики
export function updateStatsCards(data) {
    const statsCards = document.getElementById('statsCards');
    if (!statsCards) return;
    
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

// Функция создания всех графиков
export function createAllCharts(data) {
    // Уничтожаем старые графики
    Object.values(window.chartInstances).forEach(chart => {
        if (chart) chart.destroy();
    });
    
    const daysCount = data.daily.length;
    const daysFromStart = data.daily.map((_, index) => index + 1);
    const annotations = createAnnotations(daysCount);

    // Проверяем наличие canvas элементов
    const allCanvas = document.getElementById('allTouchpointsChart');
    const pieCanvas = document.getElementById('pieChart');
    const totalCanvas = document.getElementById('totalChart');
    const derivCanvas = document.getElementById('derivativesChart');
    
    if (!allCanvas || !pieCanvas || !totalCanvas || !derivCanvas) {
        console.error('Canvas элементы не найдены');
        return;
    }

    // 1. График всех тачпоинтов
    const allCtx = allCanvas.getContext('2d');
    window.chartInstances.all = new Chart(allCtx, {
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
                    max: daysCount,
                    ticks: {
                        callback: function(val) {
                            if (val % 5 === 0 || val === 1 || val === daysCount) {
                                return val;
                            }
                            return '';
                        }
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: { display: true, text: 'Количество открытий' }
                }
            }
        }
    });
    
    // 2. Круговая диаграмма
    const pieCtx = pieCanvas.getContext('2d');
    window.chartInstances.pie = new Chart(pieCtx, {
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
    
    const totalCtx = totalCanvas.getContext('2d');
    window.chartInstances.total = new Chart(totalCtx, {
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
                    max: daysCount,
                    ticks: {
                        callback: function(val) {
                            if (val % 5 === 0 || val === 1 || val === daysCount) {
                                return val;
                            }
                            return '';
                        }
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: { display: true, text: 'Количество открытий' }
                }
            }
        }
    });
    
    // 4. Производные
    const derivCtx = derivCanvas.getContext('2d');
    
    // Создаем массив индексов для отображения (каждый 5-й день)
    const displayIndices = [];
    for (let i = 0; i < daysFromStart.length; i += 5) {
        displayIndices.push(i);
    }
    if (displayIndices[displayIndices.length - 1] !== daysFromStart.length - 1) {
        displayIndices.push(daysFromStart.length - 1);
    }
    
    const derivLabels = displayIndices.map(i => daysFromStart[i]);
    const buttonDerivData = displayIndices.map(i => data.derivatives.button[i] || 0);
    const svpDerivData = displayIndices.map(i => data.derivatives.svp[i] || 0);
    const vaDerivData = displayIndices.map(i => data.derivatives.va[i] || 0);
    const appDerivData = displayIndices.map(i => data.derivatives.app[i] || 0);
    
    const allDerivValues = [
        ...buttonDerivData,
        ...svpDerivData,
        ...vaDerivData,
        ...appDerivData
    ].filter(v => !isNaN(v) && isFinite(v) && v !== null);
    
    const maxAbsDeriv = allDerivValues.length > 0 
        ? Math.max(...allDerivValues.map(Math.abs)) * 1.2 
        : 1;
    
    window.chartInstances.derivatives = new Chart(derivCtx, {
        type: 'line',
        data: {
            labels: derivLabels,
            datasets: [
                {
                    label: 'Кнопка',
                    data: buttonDerivData,
                    borderColor: '#1f77b4',
                    tension: 0.1,
                    pointRadius: 4,
                    borderWidth: 3
                },
                {
                    label: 'СВП',
                    data: svpDerivData,
                    borderColor: '#ff7f0e',
                    tension: 0.1,
                    pointRadius: 4,
                    borderWidth: 3
                },
                {
                    label: 'VA',
                    data: vaDerivData,
                    borderColor: '#2ca02c',
                    tension: 0.1,
                    pointRadius: 4,
                    borderWidth: 3
                },
                {
                    label: 'Приложение',
                    data: appDerivData,
                    borderColor: '#d62728',
                    tension: 0.1,
                    pointRadius: 4,
                    borderWidth: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                annotation: { annotations: createAnnotations(daysCount) }
            },
            scales: {
                x: { 
                    title: { display: true, text: 'День с начала релиза' },
                    min: 1,
                    max: daysCount,
                    ticks: {
                        callback: function(val) {
                            if (val % 5 === 0 || val === 1 || val === daysCount) {
                                return val;
                            }
                            return '';
                        }
                    }
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

// Функция обновления таблицы
export function updateTable(data) {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    
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

// Функция загрузки данных для главной страницы
async function loadMainPageData() {
    try {
        const response = await fetch('data.json');
        if (!response.ok) throw new Error('Ошибка загрузки');
        
        const data = await response.json();
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('statsCards').style.display = 'grid';
        document.getElementById('chartsGrid').style.display = 'grid';
        document.getElementById('dataTable').style.display = 'block';
        
        updateStatsCards(data);
        createAllCharts(data);
        updateTable(data);
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Автоматическая загрузка только для главной страницы
if (window.location.pathname.endsWith('index.html') || window.location.pathname === '/') {
    document.addEventListener('DOMContentLoaded', loadMainPageData);
}
