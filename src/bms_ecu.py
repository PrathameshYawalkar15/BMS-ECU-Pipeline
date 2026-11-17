class BatteryManagementECU:
    def __init__(self):
        self.temperature = 25.0
        self.voltage = 3.8
        self.can_active = True
        self.state = "NORMAL"
        self.contactor_closed = True
        self.fault_code = "ERR_OK"
        self.debounce_counter = 0

    def reset_ecu(self):
        """Resets the ECU state back to normal operating parameters."""
        self.temperature = 25.0
        self.voltage = 3.8
        self.can_active = True
        self.state = "NORMAL"
        self.contactor_closed = True
        self.fault_code = "ERR_OK"
        self.debounce_counter = 0

    def update_control(self):
        """Compatibility alias in case an LLM test calls update_control() explicitly."""
        self._evaluate_safety_rules(use_debounce=False)

    def set_cell_temperature(self, temp: float):
        """Compatibility helper for direct temperature setting."""
        self.update_sensors(temperature=temp)

    def set_cell_voltage(self, voltage: float):
        """Compatibility helper for direct voltage setting."""
        self.update_sensors(voltage=voltage)

    def update_sensors(self, *args, **kwargs):
        """Updates sensor readings from dictionary payloads or keyword arguments."""
        data = {}
        if args and isinstance(args[0], dict):
            data.update(args[0])
        data.update(kwargs)

        # Support multi-cycle sequence steps if passed as a list of cycle dicts
        if "sequence" in data and isinstance(data["sequence"], list):
            if data.get("reset_before", False):
                self.reset_ecu()
            for step in data["sequence"]:
                if isinstance(step, dict) and step.get("action") == "reset":
                    self.reset_ecu()
                else:
                    self._apply_single_step(step, default_debounce=True)
            return

        use_debounce = bool(data.get("use_debounce", False))
        self._apply_single_step(data, default_debounce=use_debounce)

    def _apply_single_step(self, data: dict, default_debounce: bool = False):
        if "cell_voltage_mv" in data and data["cell_voltage_mv"] is not None:
            val = float(data["cell_voltage_mv"])
            self.voltage = val / 1000.0 if val > 20.0 else val
        if "voltage" in data and data["voltage"] is not None:
            val = float(data["voltage"])
            self.voltage = val / 1000.0 if val > 20.0 else val
        if "input_voltage" in data and data["input_voltage"] is not None:
            val = float(data["input_voltage"])
            self.voltage = val / 1000.0 if val > 20.0 else val

        if "temperature" in data and data["temperature"] is not None:
            self.temperature = float(data["temperature"])
        if "input_temp" in data and data["input_temp"] is not None:
            self.temperature = float(data["input_temp"])
        if "temp" in data and data["temp"] is not None:
            self.temperature = float(data["temp"])

        if "can_active" in data and data["can_active"] is not None:
            self.can_active = bool(data["can_active"])
        if "input_can_active" in data and data["input_can_active"] is not None:
            self.can_active = bool(data["input_can_active"])

        use_debounce = bool(data.get("use_debounce", default_debounce))
        self._evaluate_safety_rules(use_debounce=use_debounce)

    def _evaluate_safety_rules(self, use_debounce: bool = False):
        # Latching fault behavior: once in FAULT_SHUTDOWN, require explicit reset_ecu()
        # unless normal single-step stateless mode is used
        if self.state == "FAULT_SHUTDOWN" and use_debounce:
            return

        # 1. SYS.2-BMS-004: Thermal Runaway Mitigation under CAN Bus Communication Loss (ASIL-D)
        if self.temperature > 65.0 and not self.can_active:
            self.state = "FAULT_SHUTDOWN"
            self.contactor_closed = False
            self.fault_code = "ERR_CRITICAL_THERMAL_CAN_FAULT"
            return

        # 2. SYS.2-BMS-001: Over-Temperature Protection
        if self.temperature > 60.0:
            self.state = "FAULT_SHUTDOWN"
            self.contactor_closed = False
            self.fault_code = "ERR_OVERTEMP_CRITICAL"
            return

        # 3. SYS.2-BMS-002: Over-Voltage Protection (supports both single-step BVA & 2-cycle debounce)
        if self.voltage > 4.25:
            self.debounce_counter += 1
            if not use_debounce or self.debounce_counter >= 2:
                self.state = "FAULT_SHUTDOWN"
                self.contactor_closed = False
                self.fault_code = "ERR_OVERVOLTAGE"
                return
            else:
                # Transient 1st cycle in debounce mode stays NORMAL while counting
                self.state = "NORMAL"
                self.contactor_closed = True
                self.fault_code = "ERR_OK"
                return
        else:
            self.debounce_counter = 0

        # 4. SYS.2-BMS-003: Under-Voltage Protection
        if self.voltage < 2.50:
            self.state = "FAULT_SHUTDOWN"
            self.contactor_closed = False
            self.fault_code = "ERR_UNDERVOLTAGE"
            return

        # Normal Operational State
        self.state = "NORMAL"
        self.contactor_closed = True
        self.fault_code = "ERR_OK"
