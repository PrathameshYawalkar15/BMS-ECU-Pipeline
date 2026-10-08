from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_002_overvoltage_isolation():
    """Test that overvoltage condition triggers proper fault state."""
    ecu = BatteryManagementECU()
    # Simulate high voltage condition exceeding threshold (4.25V)
    ecu.update_sensors(voltage=5.0)  # Above threshold
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False  # Contactor should open (False) on fault
    assert ecu.fault_code == "ERR_OVERVOLTAGE"
