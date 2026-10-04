from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_001_overtemperature_isolation():
    # 1. Instantiate ECU
    ecu = BatteryManagementECU()
    
    # 2. Update sensor inputs (using values retrieved from ChromaDB)
    ecu.update_sensors(temperature=65.0)
    
    # 3. Print telemetry for log capture
    print(f"\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    
    # 4. Assert ground-truth parameters retrieved from ChromaDB
    assert ecu.state == "FAULT", f"Expected state FAULT, got {ecu.state}"
    assert ecu.contactor_closed is False, f"Expected contactor OPEN (False), got {ecu.contactor_closed}"
    assert ecu.fault_code == "ERR_OVERTEMP_CRITICAL", f"Expected ERR_OVERTEMP_CRITICAL, got {ecu.fault_code}"