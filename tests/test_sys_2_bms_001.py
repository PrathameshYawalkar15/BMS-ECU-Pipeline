from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_001_overtemperature_isolation():
    """Test that an over-temperature condition is detected when temperature exceeds 60.0°C threshold."""
    ecu = BatteryManagementECU()
    ecu.update_sensors(temperature=65.0)
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    assert ecu.state == "FAULT", f"Expected FAULT state, got {ecu.state}"
    assert ecu.contactor_closed is False, "Contactor should be open on over-temperature"
    assert ecu.fault_code == "ERR_OVERTEMP_CRITICAL", f"Expected ERR_OVERTEMP_CRITICAL, got {ecu.fault_code}"