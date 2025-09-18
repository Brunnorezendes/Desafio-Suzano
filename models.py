from pydantic import BaseModel

class Store(BaseModel):
    id: str
    type: str
    coordinates: tuple[float, float]
    visit_duration: int
    initial_frequency: int
    baseline_profitability: float 
    profitability_freq_1: float
    profitability_freq_2: float
    profitability_freq_3: float
    profitability_freq_4: float
    profitability_freq_5: float
    profitability_freq_6: float
    def distance(self, other: 'Store') -> float:
        from math import sqrt
        return sqrt((self.coordinates[0] - other.coordinates[0]) ** 2 + 
                    (self.coordinates[1] - other.coordinates[1]) ** 2)