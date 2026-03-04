// frontend/script.js
// Глобальные переменные для хранения графиков - делаем через window
window.chartInstances = {};

export function createAllCharts(data) {
    // Уничтожаем старые графики
    Object.values(window.chartInstances).forEach(chart => {
        if (chart) chart.destroy();
    });
    
    // ... весь остальной код функции createAllCharts без изменений
    // (копируйте сюда ваш существующий код)
}

export function updateStatsCards(data) {
    // ... ваш существующий код
}

export function updateTable(data) {
    // ... ваш существующий код
}

// Функция загрузки для главной страницы (если нужно)
async function loadData() {
    try {
        console.log('Загрузка данных...');
        const response = await fetch('data.json');
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

// Автозагрузка для главной страницы
if (window.location.pathname.endsWith('index.html') || window.location.pathname === '/') {
    document.addEventListener('DOMContentLoaded', loadData);
}
