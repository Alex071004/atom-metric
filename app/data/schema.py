"""Схема данных и контракты."""
from dataclasses import dataclass
from datetime import date
import pandas as pd
from typing import List, Dict
import config

@dataclass
class TouchpointData:
    """Контракт данных - что мы ожидаем на входе."""
    dates: List[date]
    button: List[int]
    svp: List[int]
    va: List[int]
    app: List[int]
    
    def to_dataframe(self) -> pd.DataFrame:
        """Конвертация в DataFrame."""
        df = pd.DataFrame({
            'date': self.dates,
            'button': self.button,
            'svp': self.svp,
            'va': self.va,
            'app': self.app
        })
        return df
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> 'TouchpointData':
        """Создание из DataFrame."""
        return cls(
            dates=df['date'].tolist(),
            button=df['button'].tolist(),
            svp=df['svp'].tolist(),
            va=df['va'].tolist(),
            app=df['app'].tolist()
        )
    
    def validate(self) -> bool:
        """Валидация данных."""
        # Все списки одной длины
        lengths = [len(self.dates), len(self.button), len(self.svp), 
                   len(self.va), len(self.app)]
        if len(set(lengths)) != 1:
            return False
        
        # Все значения неотрицательные
        for values in [self.button, self.svp, self.va, self.app]:
            if any(v < 0 for v in values):
                return False
        
        return True