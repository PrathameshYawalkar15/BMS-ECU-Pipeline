import os
import re
import json
import sys
import subprocess
import argparse
from datetime import datetime
from typing import TypedDict, Annotated, Sequence, Literal, List
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import chromadb

# Load environment variables
load_dotenv()

EXECUTION_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
PASSED_REPORT_PATH = f"reports/passed_report_{EXECUTION_TIMESTAMP}.html"
FAILED_REPORT_PATH = f"reports/failed_report_{EXECUTION_TIMESTAMP}.html"

# --- 1. Tools for Agentic RAG ---

@tool
def query_chromadb_requirement(req_id: str) -> str:
    """Queries ChromaDB vector database for ASPICE safety limits, metrics, and thresholds by Requirement ID (e.g., 'SYS.2-BMS-001')."""
    client = chromadb.PersistentClient(path="./bms_vector_store")
    try:
        collection = client.get_collection("aspice_requirements")
        results = collection.get(ids=[req_id])
        if results["metadatas"] and len(results["metadatas"]) > 0:
            return json.dumps(results["metadatas"][0])
        return f"No requirement metadata found for ID: {req_id}"
    except Exception as e:
        return f"Error querying vector store: {str(e)}"

@tool
def execute_pytest_suite(test_code: str, req_id: str = "SYS_2_BMS_001") -> str:
    """Saves generated test code to a versioned requirement test file (e.g., tests/test_sys_2_bms_001.py)
    and executes PyTest for this specific requirement asset."""
    
    os.makedirs("tests", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    clean_code = test_code
    if "```python" in clean_code:
        clean_code = clean_code.split("```python")[1].split("```")[0].strip()
    elif "```" in clean_code:
        clean_code = clean_code.split("```")[1].split("```")[0].strip()

    # Reject invalid code structure before execution
    if "BatteryManagementECU" not in clean_code or "open(" in clean_code or "inspect." in clean_code:
        return json.dumps({
            "passed": False,
            "stdout": "",
            "stderr": "REJECTED: Code must instantiate `BatteryManagementECU` without inspecting source files.",
            "is_system_error": True
        })

    safe_req_name = re.sub(r'[^a-zA-Z0-9]', '_', req_id).lower()
    target_test_file = f"tests/test_{safe_req_name}.py"

    with open(target_test_file, "w", encoding="utf-8") as f:
        f.write(clean_code)

    print(f"[PIPELINE] Saved test asset: {target_test_file}")

    # Run PyTest on the current target requirement file
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            "-rP",
            "-o", "pythonpath=.",
            "-o", "log_cli=true",
            target_test_file
        ],
        capture_output=True,
        text=True
    )

    return json.dumps({
        "passed": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "target_file": target_test_file,
        "is_system_error": False
    })


tools = [query_chromadb_requirement, execute_pytest_suite]

# --- 2. OpenRouter Model Setup ---

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY is missing in environment or .env file.")

llm = ChatOpenAI(
    model="openrouter/free",
    openai_api_key=api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
).bind_tools(tools)

# --- 3. State Definition ---

class AgenticRAGState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    retry_count: int
    requirement_id: str
    is_system_error: bool
    test_passed: bool

# --- 4. Node Definitions ---

SYSTEM_PROMPT = """You are an Autonomous AI QA Engineering Agent for an EV Battery Management System (BMS).
Your goal is to verify ASPICE functional safety requirements by generating permanent PyTest files and executing them against a simulated ECU.

WORKFLOW:
1. Call `query_chromadb_requirement(req_id)` to retrieve requirement parameters.
2. Generate a dedicated PyTest function targeting that requirement.
3. Call `execute_pytest_suite(test_code, req_id)` to save and run the test.

REQUIRED TEST TEMPLATE:
```python
from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_001_overtemperature_isolation():
    ecu = BatteryManagementECU()
    ecu.update_sensors(temperature=65.0)
    print(f"\\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    assert ecu.state == "FAULT"
    assert ecu.contactor_closed is False
    assert ecu.fault_code == "ERR_OVERTEMP_CRITICAL"
```"""

def agent_reasoning_node(state: AgenticRAGState) -> AgenticRAGState:
    response = llm.invoke(state["messages"])
    return {
        "messages": [response],
        "retry_count": state.get("retry_count", 0),
        "requirement_id": state.get("requirement_id", ""),
        "is_system_error": state.get("is_system_error", False),
        "test_passed": state.get("test_passed", False)
    }

def tool_execution_node(state: AgenticRAGState) -> AgenticRAGState:
    last_message = state["messages"][-1]
    tool_outputs = []
    retry_inc = 0
    is_sys_err = state.get("is_system_error", False)
    test_passed = False

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name == "query_chromadb_requirement":
            res = query_chromadb_requirement.invoke(tool_args)
        elif tool_name == "execute_pytest_suite":
            res = execute_pytest_suite.invoke(tool_args)
            retry_inc = 1
            
            try:
                res_data = json.loads(res)
                test_passed = res_data.get("passed", False)
                if res_data.get("is_system_error"):
                    is_sys_err = True
            except Exception:
                pass
        else:
            res = f"Tool '{tool_name}' not recognized."

        tool_outputs.append(ToolMessage(content=str(res), tool_call_id=tool_call["id"]))

    return {
        "messages": tool_outputs,
        "retry_count": state.get("retry_count", 0) + retry_inc,
        "requirement_id": state.get("requirement_id", ""),
        "is_system_error": is_sys_err,
        "test_passed": test_passed
    }

# --- 5. Conditional Routing ---

def should_continue(state: AgenticRAGState) -> Literal["tools", "end"]:
    # Halts graph loop only if system API breaks (not for standard assertion failures)
    if state.get("is_system_error", False):
        print("[CIRCUIT BREAKER] System error detected. Halting requirement loop.")
        return "end"

    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        if state.get("retry_count", 0) >= 3:
            print("\n[Agentic RAG] Maximum retries (3) reached.")
            return "end"
        return "tools"

    return "end"

# --- 6. Graph Compilation ---

def build_agentic_rag_graph():
    workflow = StateGraph(AgenticRAGState)
    workflow.add_node("agent", agent_reasoning_node)
    workflow.add_node("tools", tool_execution_node)

    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()

# --- 7. Dual Report Generator ---

def generate_partitioned_reports(results_map: dict):
    """Executes PyTest separately over Passed vs. Failed assets to create dedicated QA HTML reports."""
    passed_files = [res["file"] for res in results_map.values() if res["status"] == "PASSED" and res["file"]]
    failed_files = [res["file"] for res in results_map.values() if res["status"] == "FAILED" and res["file"]]

    os.makedirs("reports", exist_ok=True)

    print("\n==================================================")
    print("        GENERATING PARTITIONED QA REPORTS         ")
    print("==================================================")

    # 1. Passed Tests HTML Report
    if passed_files:
        print(f"📊 Generating Passed Suite Report ({len(passed_files)} tests)...")
        subprocess.run([
            sys.executable, "-m", "pytest", "-v", "-o", "pythonpath=.",
            f"--html={PASSED_REPORT_PATH}", "--self-contained-html", *passed_files
        ], capture_output=True)
        print(f"   --> Saved: {PASSED_REPORT_PATH}")
    else:
        print("ℹ️ No passed test cases to include in passed report.")

    # 2. Failed Tests HTML Report
    if failed_files:
        print(f"🚨 Generating Failed Suite Report ({len(failed_files)} tests)...")
        subprocess.run([
            sys.executable, "-m", "pytest", "-v", "-o", "pythonpath=.",
            f"--html={FAILED_REPORT_PATH}", "--self-contained-html", *failed_files
        ], capture_output=True)
        print(f"   --> Saved: {FAILED_REPORT_PATH}")
    else:
        print("🎉 No failed test cases! Failed report omitted.")

    print("==================================================\n")

# --- 8. Batch Pipeline Runner ---

def get_all_chromadb_requirement_ids() -> List[str]:
    client = chromadb.PersistentClient(path="./bms_vector_store")
    try:
        collection = client.get_collection("aspice_requirements")
        return collection.get()["ids"]
    except Exception as e:
        print(f"[CHROMADB ERROR] Could not fetch requirement IDs: {e}")
        return []

def run_batch_pipeline(requirement_ids: List[str]):
    app = build_agentic_rag_graph()
    
    print(f"\n==================================================")
    print(f" STARTING FULL BATCH TESTING: {len(requirement_ids)} REQUIREMENTS")
    print(f" Target Requirements: {', '.join(requirement_ids)}")
    print(f"==================================================\n")

    summary_results = {}

    for req_id in requirement_ids:
        print(f"\n>>> [PROCESSING REQUIREMENT]: {req_id} <<<")
        
        user_goal = f"Test ASPICE requirement {req_id} by retrieving parameters from ChromaDB and executing PyTest."
        
        initial_state = {
            "messages": [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_goal)
            ],
            "retry_count": 0,
            "requirement_id": req_id,
            "is_system_error": False,
            "test_passed": False
        }

        safe_req_name = re.sub(r'[^a-zA-Z0-9]', '_', req_id).lower()
        test_file = f"tests/test_{safe_req_name}.py"

        try:
            final_state = initial_state
            for event in app.stream(initial_state):
                for node, output in event.items():
                    print(f"--- Node Completed: {node} ---")
                    final_state = output

            if final_state.get("test_passed"):
                summary_results[req_id] = {"status": "PASSED", "file": test_file}
                print(f"✅ Requirement {req_id}: PASSED")
            else:
                summary_results[req_id] = {"status": "FAILED", "file": test_file}
                print(f"❌ Requirement {req_id}: FAILED (Logged for analysis)")

        except Exception as e:
            summary_results[req_id] = {"status": "ERROR", "file": None}
            print(f"⚠️ Exception processing {req_id}: {e}")

    # Generate Partitioned HTML Reports for QA Analysis
    generate_partitioned_reports(summary_results)

    # Print Terminal Summary
    print("==================================================")
    print("           BATCH EXECUTION SUMMARY")
    print("==================================================")
    for req, res in summary_results.items():
        status_icon = "✅" if res['status'] == "PASSED" else "❌"
        print(f"  {status_icon} {req}: {res['status']}")
    print("==================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous EV BMS QA Verification Pipeline")
    parser.add_argument("--reqs", nargs="+", help="Specify requirement IDs to run.")
    args = parser.parse_args()

    if args.reqs:
        target_requirements = args.reqs
    else:
        target_requirements = get_all_chromadb_requirement_ids()

    if not target_requirements:
        print("❌ Error: No requirements found to execute.")
        sys.exit(1)

    run_batch_pipeline(target_requirements)