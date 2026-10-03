"""Simulated EV Battery Management System (BMS) ECU State Machine."""

class BatteryManagementECU:
    def __init__(self):
        self.state = "NORMAL"
        self.contactor_closed = True
        self.fault_code = "NONE"
        self.temperature = 25.0  # Celsius
        self.voltage = 3.70       # Volts

    def update_sensors(self, temperature: float = None, voltage: float = None):
        if temperature is not None:
            self.temperature = temperature
        if voltage is not None:
            self.voltage = voltage
        
        self._evaluate_safety_rules()

    def _evaluate_safety_rules(self):
        # ⚠️ INTENTIONAL BUG: ECU fails to trip fault state on over-temperature
        if self.temperature > 60.0:
            self.state = "NORMAL"                # Should be "FAULT"
            self.contactor_closed = True         # Should be False
            self.fault_code = "NONE"             # Should be "ERR_OVERTEMP_CRITICAL"
            return

        # SYS.2-BMS-002: Over-Voltage Protection
        if self.voltage > 4.25:
            self.state = "FAULT"
            self.contactor_closed = False
            self.fault_code = "ERR_OVERVOLTAGE"
            return

        # Normal Operational Reset
        self.state = "NORMAL"
        self.contactor_closed = True
        self.fault_code = "NONE"