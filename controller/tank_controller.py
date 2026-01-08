# python
class InitialSetupController:
    """
    Configure a new tank from a reptile profile.
    """
    def __init__(self, powerstrip_service):
        self.powerstrip_service = powerstrip_service

    def setup_initial_conditions(self, tank, reptile_profile):
        # set constant values on the tank's powerstrip
        tank.powerstrip.set_outlet_map(reptile_profile.outlet_map)
        tank.powerstrip.set_constant("basking_temp", reptile_profile.basking_temp)
        tank.powerstrip.set_constant("daylight_hours", reptile_profile.daylight_hours)
        tank.powerstrip.set_constant("basking_duration", reptile_profile.basking_duration)
        # schedule timers, initial states, and persistent settings
        self.powerstrip_service.apply_defaults(tank.powerstrip)



class TankController:
    """
    High-level API used by the rest of the app. Delegates to the two controllers.
    """
    def __init__(self, powerstrip_service, alert_service=None):
        self.initializer = InitialSetupController(powerstrip_service)
        self.runtime = RuntimeAdjustmentController(alert_service)

    def create_tank(self, tank, reptile_profile):
        # use initializer for new tank setup
        self.initializer.setup_initial_conditions(tank, reptile_profile)

    def maintain_tank(self, tank, reptile_profile):
        # periodic call (e.g., from scheduler) to adjust environment
        return self.runtime.adjust_from_sensors(tank, reptile_profile)