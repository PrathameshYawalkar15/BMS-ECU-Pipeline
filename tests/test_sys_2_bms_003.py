import pytest
from src.bms_ecu import BatteryManagementECU


@pytest.mark.safety_critical
@pytest.mark.requirement("REQ_BMS_TEMP_001")
def test_cell_under_voltage_protection():
    ecu = BatteryManagementECU()
    ecu.update_sensors(voltage=2.49)
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_UNDERVOLTAGE"