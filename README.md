# Autonomous ASPICE SWE.4 & ISO 26262 Agentic V&V Pipeline for EV Battery Management Systems (BMS)

[![ASPICE BMS QA Pipeline](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME/actions/workflows/pipeline.yml/badge.svg)](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME/actions/workflows/pipeline.yml)
[![ASPICE v3.1 Compliant](https://img.shields.io/badge/ASPICE-SYS.2%20%7C%20SWE.4%20%7C%20SYS.5-blue.svg)](https://www.automotive-spice.com/)
[![Functional Safety](https://img.shields.io/badge/ISO%2026262-ASIL--C%20%2F%20ASIL--D-red.svg)](https://www.iso.org/standard/68383.html)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph Multi-Critic](https://img.shields.io/badge/LangGraph-Multi--Critic%20Workflow-00A67E.svg)](https://www.langchain.com/langgraph)
[![Ollama Local LLM](https://img.shields.io/badge/LLM-Qwen2.5--Coder%207B-orange.svg)](https://ollama.com/)
[![Docker Containerized](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

An enterprise-grade, hybrid **Deterministic + Agentic Software Verification & Validation (V&V) Pipeline** engineered for **Automotive SPICE (ASPICE v3.1 SWE.4 / SYS.5)** and **ISO 26262 (ASIL-C / ASIL-D)** compliance in Electric Vehicle (EV) Battery Management Systems (BMS).

Standard LLM test generators fail in safety-critical automotive engineering because they hallucinate decimal boundary math, invent non-existent ECU methods, or omit required safety assertions. This platform solves that by combining a **Pydantic Input-Quality Gate**, a **Deterministic Boundary Value Analysis (BVA) & Stateful Multi-Cycle Debounce Engine**, an **Incremental SHA-256 Verification Cache**, and a **3-Critic LangGraph State Machine** powered locally by **Ollama (`qwen2.5-coder:7b`)** to guarantee 100% mathematically sound, traceable, and executable PyTest suites.

---

## 🏛️ End-to-End System Architecture

The pipeline implements the Automotive **V-Model**, bridging **SYS.2 System Requirements Analysis** directly to **SWE.4 Software Unit Verification** and **SYS.5 System Integration Testing** with complete bidirectional traceability.

```text
  [1. SAFETY REQUIREMENTS] (aspice_requirements.json)
   Single Source of Truth (SSOT) for ASIL-C / ASIL-D BMS safety rules
               │
               ▼
  [2. INPUT QUALITY GATE] (src/requirement_schema.py - Pydantic)
   Validates requirement IDs, ASIL ratings, threshold math operators, and scenario schemas
               │
               ▼
  [3. DETERMINISTIC MATH & STATEFUL ENGINE] (src/bva_engine.py + Pipeline Enricher)
   Zero LLM guesswork! Python deterministically computes & injects:
   ├── Boundary Value Analysis (BVA): (Threshold - Step), (Exact Threshold), (Threshold + Step)
   └── Stateful Multi-Cycle Sequences: 1-Cycle Spike Tolerance, 2-Cycle Debounce Trip, & ECU Reset Recovery
               │
               ▼
  [4. INCREMENTAL SHA-256 CACHE] (verification_state.json)
   Computes canonical SHA-256 digest of enriched requirement + vectors:
   ├── UNCHANGED ──► Reuses existing verified PyTest file (Zero LLM compute overhead)
   └── MODIFIED  ──► Triggers Stateful LangGraph Multi-Critic Workflow:
               │
               ▼
  ┌────────────────────────────────────────────────────────────────────────────┐
  │                 5. LANGGRAPH MULTI-CRITIC AGENT WORKFLOW                   │
  │                                                                            │
  │   ┌────────────────────────────────────────────────────────────────────┐   │
  │   │ [Generator Node] (ChatOllama: qwen2.5-coder:7b @ temperature=0)    │   │
  │   │ Synthesizes @pytest.mark.parametrize suite from enriched matrix    │   │
  │   └─────────────────────────────────┬──────────────────────────────────┘   │
  │                                     │                                      │
  │            ┌────────────────────────┼────────────────────────┐             │
  │            ▼                        ▼                        ▼             │
  │  ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐   │
  │  │     Critic 1:     │    │     Critic 2:     │    │     Critic 3:     │   │
  │  │   Traceability    │    │  API & AST Syntax │    │ ISO 26262 Safety  │   │
  │  │  (ASPICE SWE.4)   │    │ (ast.parse & call │    │ (State, Contactor │   │
  │  │ Markers & vectors │    │ contract check)   │    │ & Fault asserts)  │   │
  │  └─────────┬─────────┘    └─────────┬─────────┘    └─────────┬─────────┘   │
  │            └────────────────────────┼────────────────────────┘             │
  │                                     ▼                                      │
  │                        ┌─────────────────────────┐                         │
  │                        │ [Critic Aggregator Gate]│                         │
  │                        └────────────┬────────────┘                         │
  │                                     │                                      │
  │      ├── Any Critic Rejected? ──────┴─► Loops combined feedback to         │
  │      │                                  Generator (Max 2 Retries) or       │
  │      │                                  applies Deterministic SWE.4        │
  │      │                                  Fallback Template                  │
  │      └── All 3 Critics Approved! ─────► Writes verified test_*.py to disk  │
  └─────────────────────────────────────────────────────┬──────────────────────┘
                                                        │
                                                        ▼
  [6. DETERMINISTIC PYTEST EXECUTION] (src/bms_ecu.py)
   Executes 26+ parameterized BVA & stateful multi-cycle scenarios against BatteryManagementECU
                                                        │
                                                        ▼
  [7. PARTITIONED QA & ASPICE COMPLIANCE ARTIFACTS] (reports/)
   ├── Passed HTML Suite: reports/passed/passed_report_<TIMESTAMP>.html
   ├── Failed HTML Suite: reports/failed/failed_report_<TIMESTAMP>.html
   ├── Bidirectional Traceability Matrix: reports/compliance/traceability_matrix.json
   ├── Interactive ASPICE Dashboard: reports/compliance/aspice_compliance_report_<TIMESTAMP>.html
   └── AI Executive Audit Summary: reports/ai_audit_summary.md
```

---

## 🚀 Key Engineering Innovations

### 1. Defense-in-Depth Against LLM Hallucinations (7-Layer Guardrail System)
1. **Zero-Temperature Greedy Decoding:** Runs `ChatOllama(model="qwen2.5-coder:7b", temperature=0)` for deterministic token generation.
2. **Pydantic Input-Quality Gate (`src/requirement_schema.py`):** Halts execution immediately if `aspice_requirements.json` contains malformed schemas or missing safety attributes.
3. **Deterministic Boundary Math (`src/bva_engine.py`):** Removes floating-point math from the LLM. Python calculates exact test vectors (`threshold - step`, `threshold`, `threshold + step`) at `0.1 °C` and `0.01 V` (`10 mV`) precision along with ground-truth expected states (`NORMAL` vs `FAULT_SHUTDOWN`).
4. **Stateful Multi-Cycle Debounce & Reset Sequences:** Automatically injects multi-step timeline vectors (`"sequence"`) to verify that transient 1-cycle voltage spikes (`4.30 V`) are tolerated (`debounce_counter == 1`), 2 consecutive cycles latch `FAULT_SHUTDOWN`, and `reset_ecu()` restores normal operation.
5. **Specialized 3-Critic LangGraph Verification Gate:**
   * **Critic 1 (`traceability_critic_node`):** Verifies `@pytest.mark.requirement("<REQ_ID>")`, `@pytest.mark.parametrize`, and checks that zero scenario vectors were omitted.
   * **Critic 2 (`api_syntax_critic_node`):** Parses generated code into a Python Abstract Syntax Tree (`ast.parse` & `ast.walk`) to verify valid syntax, enforce `ecu.update_sensors(scenario)`, and block hallucinated method calls (such as `update_control` or `set_voltage`).
   * **Critic 3 (`safety_critic_node`):** Combines deterministic AST attribute checks (`ecu.state`, `ecu.contactor_closed`, `ecu.fault_code`) with an LLM semantic safety review.
6. **Closed-Loop Self-Correction:** Routes specific critic rejection reasons back to `generator_node` for targeted self-healing.
7. **Deterministic SWE.4 Fallback Template (`build_fallback_test_code`):** Guarantees 100% valid, executable test generation even if the local LLM exhausts its retry budget.

### 2. Incremental SHA-256 State Caching (`verification_state.json`)
* Computes a canonical SHA-256 hash of each enriched requirement payload (`compute_hash()`).
* Unchanged requirements bypass the LLM loop and reuse their verified test files in milliseconds—enabling rapid CI/CD regression runs across large requirement sets.

### 3. Bidirectional ASPICE SWE.4 Traceability & Partitioned Reporting
* Automatically maps **System Requirement ID $\leftrightarrow$ ASIL Rating $\leftrightarrow$ BVA & Stateful Vectors $\leftrightarrow$ Multi-Critic Verdicts $\leftrightarrow$ PyTest Execution Status**.
* Produces self-contained `pytest-html` reports partitioned into `reports/passed/` and `reports/failed/` alongside an executive ASPICE compliance dashboard (`reports/compliance/`).

---

## 🛠️ Tech Stack & Automotive Standards

| Domain | Technologies / Standards |
| :--- | :--- |
| **Automotive Standards** | ASPICE v3.1 (SYS.2, SWE.4, SYS.5, SUP.9), ISO 26262 Part 6 (ASIL-C to ASIL-D) |
| **Multi-Agent Orchestration** | LangGraph (`StateGraph`), LangChain (`langchain-ollama`) |
| **Local LLM Inference** | Ollama (`qwen2.5-coder:7b`, `temperature=0`) |
| **Data Validation & Math** | Pydantic v2 (`RequirementModel`), Deterministic BVA Engine, Python `ast` |
| **Verification & Reporting** | PyTest, `pytest-html`, Custom ASPICE HTML/JSON/Markdown Traceability Generators |
| **DevOps & Environment** | Python 3.11+, Docker, Docker Compose, GitHub Actions |

---

## 📂 Project Structure

```text
BMS-ECU-Pipeline/
├── .github/
│   └── workflows/
│       └── pipeline.yml                  # Automated CI/CD verification workflow
├── reports/
│   ├── passed/                           # Partitioned HTML reports for passing test suites
│   ├── failed/                           # Partitioned HTML reports for failing test suites
│   ├── compliance/
│   │   ├── aspice_compliance_report_*.html # Interactive ASPICE SWE.4 & ISO 26262 Dashboard
│   │   └── traceability_matrix.json      # Bidirectional traceability JSON artifact
│   └── ai_audit_summary.md               # Executive Markdown audit summary
├── src/
│   ├── bms_ecu.py                        # Simulated BMS ECU State Machine (BVA + 2-Cycle Debounce + Reset)
│   ├── bva_engine.py                     # Deterministic Boundary Value Analysis (BVA) math engine
│   ├── requirement_schema.py             # Pydantic input-quality gate schema definitions
│   ├── generate_audit_report.py          # ASPICE SWE.4 HTML Compliance Dashboard generator
│   ├── ollama_auditor.py                 # AI executive audit summary generator
│   └── run_pipeline_4.py                 # Main Multi-Critic LangGraph Orchestrator & Test Runner
├── tests/                                # Auto-generated parameterized PyTest suites (test_sys_2_bms_*.py)
├── aspice_requirements.json              # Single Source of Truth (SSOT) for BMS safety requirements
├── verification_state.json               # SHA-256 incremental manifest cache & critic verdicts
├── Dockerfile                            # Production container specification
├── docker-compose.yml                    # Container orchestration
├── requirements.txt                      # Locked Python dependencies
└── README.md                             # Project documentation
```

---

## 📋 ISO 26262 & ASPICE SWE.4 Safety Verification Matrix

Across the **4 core system requirements**, the pipeline deterministically synthesizes and executes **26+ parameterized verification scenarios** covering nominal operation, exact BVA limits, multi-cycle debounce persistence, and fault-latch reset recovery:

| Requirement ID | Module / Safety Title | ASIL | Target Metric & Rule | BVA & Stateful Vectors Verified | Expected ECU Fault State & Code |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **SYS.2-BMS-001** | Cell Over-Temperature Isolation | **ASIL-D** | `temperature > 60.0 °C` | Nominal, Fault, BVA (`59.9°C`, `60.0°C`, `60.1°C`), Fault $\rightarrow$ `reset_ecu()` $\rightarrow$ Normal Recovery | `FAULT_SHUTDOWN` (`contactor=False`)<br>`ERR_OVERTEMP_CRITICAL` |
| **SYS.2-BMS-002** | Cell Over-Voltage Protection (with 2-Cycle Debounce) | **ASIL-C** | `voltage > 4.25 V` | Nominal, Fault, BVA (`4.24V`, `4.25V`, `4.26V`), 1-Cycle Spike Tolerated, Transient Spike Recovery, 2-Cycle Consecutive Trip, Fault $\rightarrow$ Reset Recovery | `FAULT_SHUTDOWN` (`contactor=False`)<br>`ERR_OVERVOLTAGE` |
| **SYS.2-BMS-003** | Cell Under-Voltage Protection | **ASIL-D** | `voltage < 2.50 V` | Nominal, Fault, BVA (`2.49V`, `2.50V`, `2.51V`) | `FAULT_SHUTDOWN` (`contactor=False`)<br>`ERR_UNDERVOLTAGE` |
| **SYS.2-BMS-004** | Thermal Runaway Mitigation under CAN Loss | **ASIL-D** | `temperature > 65.0 °C` **AND** `can_active == False` | Nominal (`45°C`, CAN=True), High Temp with CAN Active (`66°C`, CAN=True), Critical Thermal + CAN Loss (`66°C`, CAN=False) | `FAULT_SHUTDOWN` (`contactor=False`)<br>`ERR_CRITICAL_THERMAL_CAN_FAULT` |

*(Note: In all `"NORMAL"` operating states, `BatteryManagementECU` maintains `contactor_closed = True` and `fault_code = "ERR_OK"`).*

---

## 🚦 Quick Start Guide

### Prerequisites
1. **Python `3.11+`** installed.
2. **Ollama** installed and running locally ([https://ollama.com](https://ollama.com)) with the `qwen2.5-coder:7b` model pulled:
   ```bash
   ollama pull qwen2.5-coder:7b
   ```

### 1. Local Environment Setup

```powershell
# Clone repository
git clone https://github.com/YOUR_GITHUB_USERNAME/BMS-ECU-Pipeline.git
cd BMS-ECU-Pipeline

# Create and activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Or on Linux / macOS:
# python3 -m venv venv && source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Full Multi-Critic V&V Pipeline

#### Fresh Full Generation Run (Clears Cache & Regenerates All Tests)
```powershell
# Windows PowerShell
Remove-Item -Path tests\*.py -Force -ErrorAction SilentlyContinue
Remove-Item -Path verification_state.json -Force -ErrorAction SilentlyContinue
python src/run_pipeline_4.py
```

```bash
# Linux / macOS
rm -f tests/*.py verification_state.json
python src/run_pipeline_4.py
```

#### Incremental Cached Run (Only Regenerates Modified Requirements)
```bash
python src/run_pipeline_4.py
```

### 3. Run Generated PyTest Suite Directly
```bash
python -m pytest -v -o pythonpath=. tests/
```

---

## 📊 Generated Compliance & QA Artifacts

Every pipeline run produces four audit-ready artifacts inside `reports/`:

1. **Interactive ASPICE SWE.4 Compliance Dashboard:**  
   `reports/compliance/aspice_compliance_report_<TIMESTAMP>.html`  
   Displays requirement coverage cards, ASIL ratings, BVA/stateful vector tags, individual verdicts from all 3 critics (`Traceability`, `API_Syntax`, `ISO26262_Safety`), and execution badges.
2. **Bidirectional Traceability Matrix (JSON):**  
   `reports/compliance/traceability_matrix.json`  
   Machine-readable audit trail linking requirement specs to test files and scenario vectors.
3. **Partitioned PyTest HTML Reports:**  
   * `reports/passed/passed_report_<TIMESTAMP>.html`
   * `reports/failed/failed_report_<TIMESTAMP>.html`
4. **AI Audit Summary (Markdown):**  
   `reports/ai_audit_summary.md`

---

## 🐳 Docker Containerized Execution

```bash
# Build and run the verification pipeline in a container
docker compose up --build
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.