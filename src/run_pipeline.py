import os
import re
import json
import hashlib
import subprocess
import sys
from datetime import datetime
from langchain_ollama import ChatOllama

EXECUTION_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
PASSED_REPORT_PATH = f"reports/passed_report_{EXECUTION_TIMESTAMP}.html"
FAILED_REPORT_PATH = f"reports/failed_report_{EXECUTION_TIMESTAMP}.html"
MANIFEST_PATH = "verification_state.json"

# Initialize Qwen2.5-Coder for superior code generation
llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0)

def compute_hash(requirement_dict: dict) -> str:
    """Computes a SHA-256 hash of a requirement's content to detect changes."""
    req_string = json.dumps(requirement_dict, sort_keys=True)
    return hashlib.sha256(req_string.encode("utf-8")).hexdigest()

def load_manifest() -> dict:
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_manifest(manifest: dict):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

def generate_test_with_qwen(req: dict) -> str:
    """Uses Qwen2.5-Coder to generate precise PyTest code for a given ASPICE requirement."""
    prompt = f"""You are an expert automotive software verification engineer. Write a clean, executable Python PyTest test for the following EV Battery Management System (BMS) requirement.

Requirement ID: {req['req_id']}
Title: {req['title']}
Description: {req['description']}
Parameters: {json.dumps(req['parameters'])}

CRITICAL API RULES:
- Import ECU: `from src.bms_ecu import BatteryManagementECU`
- Initialize: `ecu = BatteryManagementECU()`
- Update sensors: `ecu.update_sensors(...)` using parameters from the requirement.
- Assert attributes directly:
  * `assert ecu.state == "FAULT"` (or `"FAULT_SHUTDOWN"`, `"NORMAL"`)
  * `assert ecu.contactor_closed is False`
  * `assert ecu.fault_code == "..."`
- Output ONLY valid Python code block wrapped in ```python ... ```. Do not include extra conversational filler.
"""
    response = llm.invoke(prompt)
    content = response.content

    # Extract code block safely
    if "```python" in content:
        content = content.split("```python")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
        
    return content

def run_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "aspice_requirements.json")

    if not os.path.exists(json_path):
        print(f"❌ Error: {json_path} not found.")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        requirements = json.load(f)

    manifest = load_manifest()
    os.makedirs("tests", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    print("\n==================================================")
    print("      INCREMENTAL ARCHITECTURE V&V PIPELINE       ")
    print("==================================================")

    test_files_to_execute = {}
    manifest_updated = False

    for req in requirements:
        req_id = req["req_id"]
        current_hash = compute_hash(req)
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', req_id).lower()
        test_file_path = f"tests/test_{safe_name}.py"

        cached_entry = manifest.get(req_id, {})
        is_changed = cached_entry.get("hash") != current_hash
        file_exists = os.path.exists(test_file_path)

        if not is_changed and file_exists:
            print(f"  [*] [{req_id}] Unchanged -> Reusing existing test file.")
            test_files_to_execute[req_id] = test_file_path
        else:
            print(f"  🤖 [{req_id}] New or Modified -> Generating test via Qwen2.5-Coder...")
            test_code = generate_test_with_qwen(req)
            
            # AST Validation check
            try:
                compile(test_code, test_file_path, 'exec')
            except Exception as e:
                print(f"    ⚠️ AST Syntax Error in generated code: {e}. Falling back to safe template.")
                test_code = f"from src.bms_ecu import BatteryManagementECU\n\ndef test_{safe_name}():\n    ecu = BatteryManagementECU()\n    ecu.update_sensors(temperature=65.0)\n    assert ecu.state == 'FAULT'\n"

            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(test_code)

            # Update manifest state
            manifest[req_id] = {
                "hash": current_hash,
                "file": test_file_path,
                "last_updated": datetime.now().isoformat()
            }
            manifest_updated = True
            test_files_to_execute[req_id] = test_file_path

    if manifest_updated:
        save_manifest(manifest)
        print("  💾 Verification state manifest updated.")

    # 4. Pure Python Execution Phase (Zero AI involvement)
    print("\n==================================================")
    print("           DETERMINISTIC PYTEST EXECUTION         ")
    print("==================================================")

    detailed_results = {}
    summary_counts = {"PASSED": 0, "FAILED": 0, "ERROR": 0}
    passed_files = []
    failed_files = []

    for req_id, file_path in test_files_to_execute.items():
        print(f"  Running test for {req_id}...", end="", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "-o", "pythonpath=.", file_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            summary_counts["PASSED"] += 1
            detailed_results[req_id] = {"status": "PASSED", "file": file_path}
            passed_files.append(file_path)
            print(" ✅ PASSED")
        else:
            summary_counts["FAILED"] += 1
            detailed_results[req_id] = {"status": "FAILED", "file": file_path}
            failed_files.append(file_path)
            print(" ❌ FAILED")

    # 5. Partitioned HTML Reports Generation
    print("\n==================================================")
    print("        GENERATING PARTITIONED QA REPORTS         ")
    print("==================================================")

    if passed_files:
        subprocess.run([
            sys.executable, "-m", "pytest", "-v", "-o", "pythonpath=.",
            f"--html={PASSED_REPORT_PATH}", "--self-contained-html", *passed_files
        ], capture_output=True)
        print(f"   --> Passed Report Saved: {PASSED_REPORT_PATH}")

    if failed_files:
        subprocess.run([
            sys.executable, "-m", "pytest", "-v", "-o", "pythonpath=.",
            f"--html={FAILED_REPORT_PATH}", "--self-contained-html", *failed_files
        ], capture_output=True)
        print(f"   --> Failed Report Saved: {FAILED_REPORT_PATH}")

    print("==================================================")
    print("           BATCH EXECUTION SUMMARY")
    print("==================================================")
    for req, res in detailed_results.items():
        icon = "✅" if res['status'] == "PASSED" else "❌"
        print(f"  {icon} {req}: {res['status']}")
    print(f"\n  Total Passed : {summary_counts['PASSED']}")
    print(f"  Total Failed : {summary_counts['FAILED']}")
    print(f"  Total Errors : {summary_counts['ERROR']}")
    print("==================================================\n")

if __name__ == "__main__":
    run_pipeline()