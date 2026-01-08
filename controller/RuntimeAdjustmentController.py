# python
class RuntimeAdjustmentController:
    """
    Adjust the environment based on periodic sensor readings.
    """
    def __init__(self, alert_service=None):
        self.alert_service = alert_service

    def adjust_from_sensors(self, tank, reptile_profile):
        readings = tank.get_habitat_readings()
        actions = []

        # temperature control example
        if readings.temperature < reptile_profile.min_temp:
            tank.powerstrip.turn_on("tank_heater")
            actions.append("heater_on")
        elif readings.temperature > reptile_profile.max_temp:
            tank.powerstrip.turn_off("basking_lamp")
            actions.append("basking_off")

        # humidity control example
        if readings.humidity < reptile_profile.min_humidity:
            tank.powerstrip.turn_on("Humidifier")
            actions.append("humidifier_on")
        elif readings.humidity > reptile_profile.max_humidity:
            tank.powerstrip.turn_off("Humidifier")
            actions.append("humidifier_off")

        # alert for extreme conditions
        if readings.temperature < reptile_profile.critical_low or readings.temperature > reptile_profile.critical_high:
            if self.alert_service:
                self.alert_service.send_alert(tank.id, "critical_temperature", readings.temperature)

        return actions, readings