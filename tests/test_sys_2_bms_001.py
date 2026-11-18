import pytest
from src.bms_ecu import BatteryManagementECU

SCENARIOS = [{'name': 'nominal_safe_temperature', 'input_temp': 45.0, 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}, {'name': 'boundary_exact_threshold', 'input_temp': 60.0, 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}, {'name': 'fault_over_temperature', 'input_temp': 61.0, 'expected_state': 'FAULT_SHUTDOWN', 'expected_contactor': False, 'expected_fault': 'ERR_OVERTEMP_CRITICAL'}, {'name': 'below_threshold_nominal_safe', 'input_temp': 64.9, 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}, {'name': 'exact_threshold_boundary_edge', 'input_temp': 65.0, 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}, {'name': 'above_threshold_fault_trip', 'input_temp': 65.1, 'expected_state': 'FAULT_SHUTDOWN', 'expected_contactor': False, 'expected_fault': 'ERR_OVERTEMP_CRITICAL'}, {'name': 'stateful_overtemp_fault_and_ecu_reset_recovery', 'sequence': [{'temperature': 65.0}, {'action': 'reset'}, {'temperature': 25.0}], 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}]

@pytest.mark.requirement("SYS.2-BMS-001")
@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s.get("name", f"s{i}") for i, s in enumerate(SCENARIOS)])
def test_sys_2_bms_001(scenario):
    ecu = BatteryManagementECU()
    ecu.update_sensors(scenario)
    assert ecu.state == scenario["expected_state"]
    assert ecu.contactor_closed == scenario["expected_contactor"]
    expected_fault = scenario.get("expected_fault") or "ERR_OK"
    assert ecu.fault_code == expected_fault
