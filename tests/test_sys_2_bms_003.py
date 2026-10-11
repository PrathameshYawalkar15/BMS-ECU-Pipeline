from src.bms_ecu import BatteryManagementECU

def test_003_underVoltage_isolation():
    """ASPICE SYS.2-BMS-003: Under-voltage isolation (ASIL-D) - threshold: 2.5V, fault: ERR_UNDERVOLTAGE."""
    ecu = BatteryManagementECU()
    ecu.update_sensors(voltage=2.0)
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_UNDERVOLTAGE"