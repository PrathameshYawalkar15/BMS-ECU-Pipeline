import pytest
from src.bms_ecu import BatteryManagementECU


@pytest.mark.safety_critical
@pytest.mark.requirement("REQ_BMS_TEMP_001")
def test_cell_over_temperature_isolation():
    ecu = BatteryManagementECU()
    ecu.update_sensors(temperature=61.0)
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_OVERTEMP_CRITICAL"