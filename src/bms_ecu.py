"""Simulated EV Battery Management System (BMS) ECU State Machine."""

class BatteryManagementECU:
    def __init__(self):
        self.state = "NORMAL"
        self.contactor_closed = True
        self.can_active = True
        self.temperature = 25.0  # Celsius
        self.voltage = 3.70      # Volts
        self.fault_code = "ERR_OK"

    def update_sensors(self, temperature: float = None, voltage: float = None, can_active: bool = None):
        if temperature is not None:
            self.temperature = temperature
        if voltage is not None:
            self.voltage = voltage
        if can_active is not None:
            self.can_active = can_active
        
        self._evaluate_safety_rules()

    def _evaluate_safety_rules(self):
        # SYS.2-BMS-004: Thermal Runaway Mitigation under CAN Bus Communication Loss (ASIL-D)
        if self.temperature > 65.0 and not self.can_active:
            self.state = "FAULT_SHUTDOWN"
            self.contactor_closed = False
            self.fault_code = "ERR_CRITICAL_THERMAL_CAN_FAULT"
            return

        # SYS.2-BMS-001: Over-Temperature Protection (Fixed intentional bug for compliance)
        if self.temperature > 60.0:
            self.state = "FAULT"
            self.contactor_closed = False
            self.fault_code = "ERR_OVERTEMP_CRITICAL"
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
        self.fault_code = "ERR_OK"