from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_004_critical_thermal_can_fault():
    """Test that high temperature with inactive CAN produces the correct combined fault code."""
    ecu = BatteryManagementECU()
    ecu.update_sensors(temperature=65.0, can_active=False)
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    # Requirement SYS.2-BMS-004: temp > 65.0 AND can_active == False -> ERR_CRITICAL_THERMAL_CAN_FAULT
    assert ecu.fault_code == "ERR_CRITICAL_THERMAL_CAN_FAULT", f"Expected ERR_CRITICAL_THERMAL_CAN_FAULT but got {ecu.fault_code}"