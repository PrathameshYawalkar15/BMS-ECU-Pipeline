import json
from pathlib import Path
from langchain_ollama import ChatOllama

def generate_ai_audit_summary():
    root = Path(__file__).parent.parent
    matrix_path = root / "bms_traceability_matrix.json"
    report_dir = root / "reports"
    report_dir.mkdir(exist_ok=True)
    
    if not matrix_path.exists():
        print("[Ollama Auditor] Traceability matrix not found, skipping AI summary.")
        return

    traceability_data = json.loads(matrix_path.read_text())
    
    prompt = f"""
    You are a Lead Functional Safety and V&V Engineer auditing an EV Battery Management System (BMS) against ASPICE SWE.4 standards.
    Here is the test traceability execution result:
    {json.dumps(traceability_data, indent=2)}

    Please write a concise Executive Verification Summary (under 150 words) evaluating safety compliance, test outcomes, and readiness for ISO 26262 audit.
    """

    try:
        llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0.1)
        response = llm.invoke(prompt)
        summary_text = response.content
        
        summary_path = report_dir / "ai_audit_summary.md"
        summary_path.write_text(f"# AI-Generated ASPICE Audit Summary\n\n{summary_text}")
        print(f"[Ollama Auditor] AI audit summary written to {summary_path}")
    except Exception as e:
        print(f"[Ollama Auditor] Could not reach local Ollama model: {e}")

if __name__ == "__main__":
    generate_ai_audit_summary()