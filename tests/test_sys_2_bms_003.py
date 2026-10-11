from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_003_under_voltage_isolation():
    """ASPICE SYS.2-BMS-003: Open contactor and raise fault when battery voltage falls below 2.5V threshold (ASIL-D)."""
    ecu = BatteryManagementECU()
    ecu.update_sensors(voltage=2.0)
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_UNDERVOLTAGE"

    ecu.update_sensors(voltage=3.0)
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    assert ecu.contactor_closed is True
    assert ecu.fault_code == "OK"