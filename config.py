from datetime import datetime, timedelta

DAYS = 90
TREND_DAYS = 60
CARS_COUNT = 100
AVG_OPENINGS_PER_CAR_PER_DAY = 20
TOTAL_AVG_OPENINGS = CARS_COUNT * AVG_OPENINGS_PER_CAR_PER_DAY

START_DATE = datetime.now().date() - timedelta(days=DAYS-1)

TOUCHPOINTS = ['button', 'svp', 'va', 'app']
TOUCHPOINT_NAMES_RU = {
    'button': 'Кнопка',
    'svp': 'СВП (руль)',
    'app': 'Приложение',
    'va': 'VA'
}
