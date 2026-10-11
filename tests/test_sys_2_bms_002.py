from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_002_overvoltage_protection():
    """Test overvoltage protection: When voltage exceeds 4.25V, system should enter FAULT state,
    open contactor, and set fault code to ERR_OVERVOLTAGE."""
    ecu = BatteryManagementECU()
    # Set voltage above threshold (4.25V)
    ecu.update_sensors(voltage=4.35)
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_OVERVOLTAGE"