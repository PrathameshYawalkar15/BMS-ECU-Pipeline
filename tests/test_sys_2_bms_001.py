from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_001_overtemperature_isolation():
    """
    ASPICE Requirement SYS.2-BMS-001: Overtemperature isolation
    ASIL-D: Critical fault handling for battery temperature exceeding threshold
    
    Verifies that when battery temperature exceeds 60.0°C threshold:
    - ECU enters FAULT state
    - Contactor is opened (closed=False)
    - Fault code ERR_OVERTEMP_CRITICAL is set
    """
    ecu = BatteryManagementECU()
    ecu.update_sensors(temperature=65.0)
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_OVERTEMP_CRITICAL"