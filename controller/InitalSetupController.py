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

