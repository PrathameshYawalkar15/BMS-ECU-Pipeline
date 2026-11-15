from src.bms_ecu import BatteryManagementECU

def test_cell_under_voltage_protection():
    ecu = BatteryManagementECU()
    ecu.update_sensors(voltage=2.49)
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_UNDERVOLTAGE"