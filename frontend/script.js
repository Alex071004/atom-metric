// Загрузка данных
let chartInstances = {};

async function loadData() {
    try {
        const response = await fetch('data.json');
        const data = await response.json();
        
        document.getElementById('lastUpdated').textContent = 
            `Обновлено: ${new Date(data.generated_at).toLocaleString('ru-RU')}`;
        
        updateStatsCards(data);
        updateCharts(data);
        updateTable(data);
    } catch (error) {
        console.error('Ошибка загрузки:', error);
    }
}

function updateStatsCards(data) {
    const cards = document.getElementById('statsCards');
    cards.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${data.summary.total_opens.toLocaleString()}</div>
            <div class="stat-label">Всего открытий</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${data.summary.avg_daily.toFixed(1)}</div>
            <div class="stat-label">В среднем в день</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${data.summary.max_daily}</div>
            <div class="stat-label">Макс в день</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${data.summary.days}</div>
            <div class="stat-label">Дней</div>
        </div>
    `;
}

function updateCharts(data) {
    // Уничтожаем старые графики
    Object.values(chartInstances).forEach(chart => chart.destroy());
    
    // Подготовка данных
    const dates = data.daily.map(d => d.date.slice(5)); // MM-DD
    
    // График всех тачпоинтов
    chartInstances.all = new Chart('allTouchpointsChart', {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Кнопка',
                    data: data.daily.map(d => d.button),
                    borderColor: '#1f77b4',
                    tension: 0.3
                },
                {
                    label: 'СВП',
                    data: data.daily.map(d => d.svp),
                    borderColor: '#ff7f0e',
                    tension: 0.3
                },
                {
                    label: 'VA',
                    data: data.daily.map(d => d.va),
                    borderColor: '#2ca02c',
                    tension: 0.3
                },
                {
                    label: 'Приложение',
                    data: data.daily.map(d => d.app),
                    borderColor: '#d62728',
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
    
    // Круговая диаграмма
    chartInstances.pie = new Chart('pieChart', {
        type: 'doughnut',
        data: {
            labels: Object.values(data.by_touchpoint).map(tp => tp.name),
            datasets: [{
                data: Object.values(data.by_touchpoint).map(tp => tp.total),
                backgroundColor: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            }]
        }
    });
    
    // Суммарные открытия
    chartInstances.total = new Chart('totalChart', {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Всего открытий',
                data: data.daily.map(d => d.total),
                borderColor: '#9467bd',
                fill: true,
                backgroundColor: 'rgba(148, 103, 189, 0.1)',
                tension: 0.3
            }]
        }
    });
    
    // Производные
    chartInstances.derivatives = new Chart('derivativesChart', {
        type: 'line',
        data: {
            labels: dates.slice(1),
            datasets: [
                {
                    label: 'Кнопка',
                    data: data.derivatives.button.slice(0, -1),
                    borderColor: '#1f77b4',
                    borderDash: [5, 5]
                },
                {
                    label: 'СВП',
                    data: data.derivatives.svp.slice(0, -1),
                    borderColor: '#ff7f0e',
                    borderDash: [5, 5]
                }
            ]
        }
    });
}

function updateTable(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = data.daily.slice(-10).reverse().map(day => `
        <tr>
            <td>${day.date}</td>
            <td>${day.button}</td>
            <td>${day.svp}</td>
            <td>${day.va}</td>
            <td>${day.app}</td>
            <td><strong>${day.total}</strong></td>
        </tr>
    `).join('');
}

// Запуск
loadData();
