from src.bms_ecu import BatteryManagementECU

def test_cell_over_voltage_protection():
    ecu = BatteryManagementECU()
    ecu.update_sensors(voltage=4.26)
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_OVERVOLTAGE"