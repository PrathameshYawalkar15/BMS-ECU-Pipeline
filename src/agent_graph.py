import os
import re
import json
import sys
import subprocess
from datetime import datetime
from typing import TypedDict, Annotated, Sequence, Literal
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import chromadb


EXECUTION_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_REPORT_PATH = f"reports/report_{EXECUTION_TIMESTAMP}.html"
LATEST_REPORT_PATH = "reports/latest_report.html"


# Load environment variables
load_dotenv()

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
    """Saves generated test code to a versioned requirement test file (e.g., tests/test_sys_2_bms_001.py),
    executes the FULL PyTest suite across all accumulated test files, and updates the run report."""
    
    os.makedirs("tests", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    clean_code = test_code
    if "```python" in clean_code:
        clean_code = clean_code.split("```python")[1].split("```")[0].strip()
    elif "```" in clean_code:
        clean_code = clean_code.split("```")[1].split("```")[0].strip()

    # Guardrail: Must import and test ECU
    if "BatteryManagementECU" not in clean_code or "open(" in clean_code or "inspect." in clean_code:
        return json.dumps({
            "passed": False,
            "stdout": "",
            "stderr": "REJECTED: Test code must instantiate and test `BatteryManagementECU` without inspecting source files.",
            "is_assertion_failure": False
        })

    # Sanitize req_id to form a valid filename (e.g., SYS.2-BMS-001 -> test_sys_2_bms_001.py)
    safe_req_name = re.sub(r'[^a-zA-Z0-9]', '_', req_id).lower()
    target_test_file = f"tests/test_{safe_req_name}.py"

    # Save/preserve the test file on disk
    with open(target_test_file, "w", encoding="utf-8") as f:
        f.write(clean_code)

    print(f"[PIPELINE] Saved requirement test asset to: {target_test_file}")

    # Run PyTest on the ENTIRE `tests/` directory to ensure full regression suite execution
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            "-rP",
            "-o", "pythonpath=.",
            "-o", "log_cli=true",
            f"--html={RUN_REPORT_PATH}",
            "--self-contained-html",
            "tests/"
        ],
        capture_output=True,
        text=True
    )


    # Mirror to latest_report.html pointer
    if os.path.exists(RUN_REPORT_PATH):
        with open(RUN_REPORT_PATH, "r", encoding="utf-8") as src_f:
            content = src_f.read()
        with open(LATEST_REPORT_PATH, "w", encoding="utf-8") as dst_f:
            dst_f.write(content)

    is_assertion_fail = "AssertionError" in result.stdout or "AssertionError" in result.stderr

    return json.dumps({
        "passed": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "report_path": RUN_REPORT_PATH,
        "target_file": target_test_file,
        "is_assertion_failure": is_assertion_fail
    })


tools = [query_chromadb_requirement, execute_pytest_suite]

# --- 2. OpenRouter Model Initialization ---

# --- 2. OpenRouter Model Setup ---

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY is missing in environment or .env file.")

# Use OpenRouter's free router slug which auto-detects tool-calling capabilities
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

# --- 4. Node Definitions ---

SYSTEM_PROMPT = """You are an Autonomous AI QA Engineering Agent for an EV Battery Management System (BMS).
Your goal is to verify ASPICE functional safety requirements by generating permanent, requirement-specific PyTest files and executing them against a simulated ECU.

WORKFLOW:
1. Call `query_chromadb_requirement(req_id)` to retrieve requirement parameters (e.g., threshold values, expected states).
2. Generate a dedicated PyTest function targeting that requirement.
3. Call `execute_pytest_suite(test_code, req_id)` to save the test module and execute the full regression test suite.

FORBIDDEN PATTERNS:
- DO NOT read, inspect, or print the source code of `bms_ecu.py` or `conftest.py`.
- DO NOT call or import `query_chromadb_requirement` inside the generated test file. It is an agent tool, NOT a test helper.
- DO NOT generate temporary or overwrite-only test files. Every test file will be permanently saved to disk for ASPICE regression auditability.

REQUIRED TEST TEMPLATE:
Your generated test code MUST follow this structure:

```python
from src.bms_ecu import BatteryManagementECU

def test_sys_2_bms_001_overtemperature_isolation():
    # 1. Instantiate ECU
    ecu = BatteryManagementECU()
    
    # 2. Update sensor inputs (using values retrieved from ChromaDB)
    ecu.update_sensors(temperature=65.0)
    
    # 3. Print telemetry for log capture
    print(f"\\n[TELEMETRY] State: {ecu.state} | Fault: {ecu.fault_code} | Contactor: {ecu.contactor_closed}")
    
    # 4. Assert ground-truth parameters retrieved from ChromaDB
    assert ecu.state == "FAULT", f"Expected state FAULT, got {ecu.state}"
    assert ecu.contactor_closed is False, f"Expected contactor OPEN (False), got {ecu.contactor_closed}"
    assert ecu.fault_code == "ERR_OVERTEMP_CRITICAL", f"Expected ERR_OVERTEMP_CRITICAL, got {ecu.fault_code}"
    """

def agent_reasoning_node(state: AgenticRAGState) -> AgenticRAGState:
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

    response = llm.invoke(messages)
    return {"messages": [response], "retry_count": state.get("retry_count", 0)}

def tool_execution_node(state: AgenticRAGState) -> AgenticRAGState:
    last_message = state["messages"][-1]
    tool_outputs = []
    retry_inc = 0

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name == "query_chromadb_requirement":
            res = query_chromadb_requirement.invoke(tool_args)
        elif tool_name == "execute_pytest_suite":
            res = execute_pytest_suite.invoke(tool_args)
            retry_inc = 1
        else:
            res = f"Tool '{tool_name}' not recognized."

        tool_outputs.append(ToolMessage(content=str(res), tool_call_id=tool_call["id"]))

    return {
        "messages": tool_outputs,
        "retry_count": state.get("retry_count", 0) + retry_inc
    }

# --- 5. Conditional Routing ---

def should_continue(state: AgenticRAGState) -> Literal["tools", "end"]:
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        if state.get("retry_count", 0) >= 3:
            print("\n[Agentic RAG] Maximum retries (3) reached. Halting loop.")
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

if __name__ == "__main__":
    app = build_agentic_rag_graph()

    user_goal = "Test ASPICE requirement SYS.2-BMS-001 by retrieving its parameters from ChromaDB and executing PyTest against the BMS ECU."

    initial_state = {
        "messages": [HumanMessage(content=user_goal)],
        "retry_count": 0
    }

    print("\n🚀 Starting Agentic RAG Pipeline Execution...\n")
    for event in app.stream(initial_state):
        for node, output in event.items():
            print(f"--- Node Completed: {node} ---")