import pytest
from src.bms_ecu import BatteryManagementECU

def test_thermal_runaway_mitigation():
    ecu = BatteryManagementECU()
    
    # Simulate high temperature and CAN bus communication loss
    ecu.update_sensors(temperature=66.0, can_active=False)
    
    # Assert the expected state and attributes
    assert ecu.state == "FAULT_SHUTDOWN"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_CRITICAL_THERMAL_CAN_FAULT"