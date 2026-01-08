import random


class Tank:
    def __init__(self, id, temp, humidity, light):
        self.id = id
        self.temp = temp
        self.humidity = humidity
        self.light = light

    def get_id(self):
        return self.id

    def get_temp(self):
        return random.uniform(self.temp - 2.0, self.temp + 2.0)

    def get_humidity(self):
        return random.uniform(self.humidity - 5.0, self.humidity + 5.0)

    def get_light(self):
        return True

    def set_temp(self, temp):
        self.temp = temp

    def set_humidity(self, humidity):
        self.humidity = humidity

    def set_light(self, light):
        self.light = light

    def update_readings(self):
        """Update tank values using setters with simulated fluctuations."""
        new_temp = random.uniform(self.temp - 2.0, self.temp + 2.0)
        new_humidity = random.uniform(self.humidity - 5.0, self.humidity + 5.0)
        self.set_temp(new_temp)
        self.set_humidity(new_humidity)
        self.set_light(True)

    def __str__(self):
        return f'Tank ID: {self.id}, Temp: {self.temp}, Humidity: {self.humidity}, Light: {self.light}'

    def get_habitat_readings(self):
        self.update_readings()
        return {
            'id': self.id,
            'temp': round(self.temp),
            'humidity': round(self.humidity),
            'light': self.light,
        }
