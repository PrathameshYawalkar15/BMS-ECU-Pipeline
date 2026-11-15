import json
from pathlib import Path
import sys
import pytest

# Force the project root directory into sys.path
root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# --- ASPICE Traceability Tracking Integration ---
traceability_data = []


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
  outcome = yield
  report = outcome.get_result()
  if report.when == "call":
    # Extract requirement markers (e.g., @pytest.mark.requirement("REQ_BMS_001"))
    req_markers = [
        marker.args[0] for marker in item.iter_markers(name="requirement")
    ]
    for req_id in req_markers:
      traceability_data.append({
          "requirement_id": req_id,
          "test_name": item.nodeid,
          "outcome": report.outcome,
      })


def pytest_sessionfinish(session, exitstatus):
  # Save the traceability matrix to an artifact file for ASPICE audit
  report_path = root_dir / "bms_traceability_matrix.json"
  with open(report_path, "w") as f:
    json.dump(traceability_data, f, indent=4)
  print(f"\n[ASPICE Compliance] Traceability matrix saved to {report_path}")