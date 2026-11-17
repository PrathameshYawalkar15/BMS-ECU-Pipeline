import pytest
from src.bms_ecu import BatteryManagementECU

SCENARIOS = [{'name': 'nominal_safe_voltage', 'input_voltage': 3.8, 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}, {'name': 'boundary_exact_threshold', 'input_voltage': 4.25, 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}, {'name': 'fault_over_voltage', 'input_voltage': 4.3, 'expected_state': 'FAULT_SHUTDOWN', 'expected_contactor': False, 'expected_fault': 'ERR_OVERVOLTAGE'}, {'name': 'below_threshold_nominal_safe', 'input_voltage': 4.24, 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}, {'name': 'exact_threshold_boundary_edge', 'input_voltage': 4.25, 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}, {'name': 'above_threshold_fault_trip', 'input_voltage': 4.26, 'expected_state': 'FAULT_SHUTDOWN', 'expected_contactor': False, 'expected_fault': 'ERR_OVERVOLTAGE'}, {'name': 'stateful_debounce_single_spike_tolerated', 'sequence': [{'voltage': 4.3, 'use_debounce': True}], 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}, {'name': 'stateful_debounce_transient_spike_recovery', 'sequence': [{'voltage': 4.3, 'use_debounce': True}, {'voltage': 3.8, 'use_debounce': True}], 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}, {'name': 'stateful_debounce_two_consecutive_cycles_trip', 'sequence': [{'voltage': 4.3, 'use_debounce': True}, {'voltage': 4.3, 'use_debounce': True}], 'expected_state': 'FAULT_SHUTDOWN', 'expected_contactor': False, 'expected_fault': 'ERR_OVERVOLTAGE'}, {'name': 'stateful_fault_reset_recovery_to_normal', 'sequence': [{'voltage': 4.3, 'use_debounce': True}, {'voltage': 4.3, 'use_debounce': True}, {'action': 'reset'}, {'voltage': 3.8, 'use_debounce': True}], 'expected_state': 'NORMAL', 'expected_contactor': True, 'expected_fault': 'ERR_OK'}]

@pytest.mark.requirement("SYS.2-BMS-002")
@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s.get("name", f"s{i}") for i, s in enumerate(SCENARIOS)])
def test_sys_2_bms_002(scenario):
    ecu = BatteryManagementECU()
    ecu.update_sensors(scenario)
    assert ecu.state == scenario["expected_state"]
    assert ecu.contactor_closed == scenario["expected_contactor"]
    expected_fault = scenario.get("expected_fault") or "ERR_OK"
    assert ecu.fault_code == expected_fault
