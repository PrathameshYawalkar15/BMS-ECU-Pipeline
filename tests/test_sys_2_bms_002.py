from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_002_overvoltage_isolation():
    """Test that overvoltage condition triggers proper isolation."""
    ecu = BatteryManagementECU()
    # Simulate voltage above threshold (4.25 V)
    ecu.update_sensors(voltage=5.0)
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    # Assertions based on requirement
    assert ecu.state == "FAULT", f"Expected FAULT state, got {ecu.state}"
    assert ecu.contactor_closed is False, "Contactor should remain closed during overvoltage"
    assert ecu.fault_code == "ERR_OVERVOLTAGE", f"Expected ERR_OVERVOLTAGE, got {ecu.fault_code}"
    print("✓ Test passed: Overvoltage isolation working correctly")
