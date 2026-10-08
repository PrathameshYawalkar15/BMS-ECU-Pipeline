from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_001_overtemperature_isolation():
    ecu = BatteryManagementECU()
    ecu.update_sensors(temperature=65.0)
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_OVERTEMP_CRITICAL"
