# python
# file: models/reptile.py
from typing import Optional

class ReptileProfile:
    """Species-level profile with optimal habitat variables."""
    def __init__(
        self,
        species_name: str,
        cool_temp: float,
        hot_temp: float,
        basking_temp: float,
        humidity: float,
        daylight_hours: int = 12,
        basking_duration_minutes: int = 60,
        requires_basking: bool = True,
        feed_interval_days: int = 7,
        description: str = "",
    ):
        self.species_name = species_name
        self.cool_temp = cool_temp
        self.hot_temp = hot_temp
        self.basking_temp = basking_temp
        self.humidity = humidity
        self.daylight_hours = daylight_hours
        self.basking_duration_minutes = basking_duration_minutes
        self.requires_basking = requires_basking
        self.feed_interval_days = feed_interval_days
        self.description = description

    def to_dict(self):
        return {
            "species_name": self.species_name,
            "cool_temp": self.cool_temp,
            "hot_temp": self.hot_temp,
            "basking_temp": self.basking_temp,
            "humidity": self.humidity,
            "daylight_hours": self.daylight_hours,
            "basking_duration_minutes": self.basking_duration_minutes,
            "requires_basking": self.requires_basking,
            "feed_interval_days": self.feed_interval_days,
            "description": self.description,
        }


class Reptile:
    def __init__(
        self,
        id: int,
        name: str,
        species: str,
        age_years: int,
        age_months: int,
        weight: float,
        tank_id: Optional[int] = None,
    ):
        self.id = id
        self.name = name
        self.tank_id = tank_id
        self.species = species
        self.age_years = age_years
        self.age_months = age_months
        self.weight = weight
        self.feed_interval_days = 7
        self.optimal_cool_temp = 30.0
        self.optimal_hot_temp = 35.0
        self.requires_basking = True
        self.basking_temp = 40.0
        self.daylight_hours = 12
        self.basking_duration_minutes = 60
        self.optimum_humidity = 50.0

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "tank_id": self.tank_id,
            "species": self.species,
            "age_years": self.age_years,
            "age_months": self.age_months,
            "weight": self.weight,
            "feed_interval_days": self.feed_interval_days,
            "optimal_cool_temp": self.optimal_cool_temp,
            "optimal_hot_temp": self.optimal_hot_temp,
            "requires_basking": self.requires_basking,
            "basking_temp": self.basking_temp,
            "daylight_hours": self.daylight_hours,
            "basking_duration_minutes": self.basking_duration_minutes,
            "optimum_humidity": self.optimum_humidity,
        }