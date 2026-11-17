import pytest
from src.bms_ecu import BatteryManagementECU

SCENARIOS = [
  {
    "name": "nominal_conditions",
    "input_temp": 45.0,
    "can_active": True,
    "expected_state": "NORMAL",
    "expected_contactor": True,
    "expected_fault": "ERR_OK"
  },
  {
    "name": "high_temp_with_can_active",
    "input_temp": 66.0,
    "can_active": True,
    "expected_state": "FAULT_SHUTDOWN",
    "expected_contactor": False,
    "expected_fault": "ERR_OVERTEMP_CRITICAL"
  },
  {
    "name": "critical_thermal_can_loss",
    "input_temp": 66.0,
    "can_active": False,
    "expected_state": "FAULT_SHUTDOWN",
    "expected_contactor": False,
    "expected_fault": "ERR_CRITICAL_THERMAL_CAN_FAULT"
  }
]

@pytest.mark.requirement("SYS.2-BMS-004")
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_thermal_runaway_mitigation(scenario):
    ecu = BatteryManagementECU()
    ecu.update_sensors(scenario)
    assert ecu.state == scenario["expected_state"]
    assert ecu.contactor_closed == scenario["expected_contactor"]
    expected_fault = scenario.get("expected_fault") or "ERR_OK"
    assert ecu.fault_code == expected_fault