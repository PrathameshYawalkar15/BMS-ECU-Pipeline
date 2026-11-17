import pytest
from src.bms_ecu import BatteryManagementECU

SCENARIOS = [
  {
    "name": "nominal_safe_voltage",
    "input_voltage": 3.6,
    "expected_state": "NORMAL",
    "expected_contactor": True,
    "expected_fault": "ERR_OK"
  },
  {
    "name": "boundary_exact_threshold",
    "input_voltage": 2.5,
    "expected_state": "NORMAL",
    "expected_contactor": True,
    "expected_fault": "ERR_OK"
  },
  {
    "name": "fault_under_voltage",
    "input_voltage": 2.4,
    "expected_state": "FAULT_SHUTDOWN",
    "expected_contactor": False,
    "expected_fault": "ERR_UNDERVOLTAGE"
  },
  {
    "name": "below_threshold_nominal_safe",
    "input_voltage": 2.49,
    "expected_state": "FAULT_SHUTDOWN",
    "expected_contactor": False,
    "expected_fault": "ERR_UNDERVOLTAGE"
  },
  {
    "name": "exact_threshold_boundary_edge",
    "input_voltage": 2.5,
    "expected_state": "NORMAL",
    "expected_contactor": True,
    "expected_fault": "ERR_OK"
  },
  {
    "name": "above_threshold_fault_trip",
    "input_voltage": 2.51,
    "expected_state": "NORMAL",
    "expected_contactor": True,
    "expected_fault": "ERR_OK"
  }
]

@pytest.mark.requirement("SYS.2-BMS-003")
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_cell_under_voltage_protection(scenario):
    ecu = BatteryManagementECU()
    ecu.update_sensors(scenario)
    assert ecu.state == scenario["expected_state"]
    assert ecu.contactor_closed == scenario["expected_contactor"]
    expected_fault = scenario.get("expected_fault") or "ERR_OK"
    assert ecu.fault_code == expected_fault