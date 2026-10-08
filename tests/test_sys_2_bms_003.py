from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_003_undervoltage_isolation():
    """Test that undervoltage condition triggers proper isolation."""
    ecu = BatteryManagementECU()
    # Simulate low voltage below threshold (2.5V)
    ecu.update_sensors(voltage=2.0)  # Below threshold
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_UNDERVOLTAGE"