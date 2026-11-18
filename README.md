# Autonomous Multi-Agent AI Code Verification & Self-Healing QA Platform (ASPICE SWE.4 / SUP.10 & ISO 26262)

[![ASPICE BMS QA Pipeline](https://github.com/PrathameshYawalkar15/BMS-ECU-Pipeline/actions/workflows/pipeline.yml/badge.svg)](https://github.com/PrathameshYawalkar15/BMS-ECU-Pipeline/actions/workflows/pipeline.yml)
[![ASPICE v3.1 Compliant](https://img.shields.io/badge/ASPICE-SYS.2%20%7C%20SWE.4%20%7C%20SUP.9%20%7C%20SUP.10-blue.svg)](https://www.automotive-spice.com/)
[![Functional Safety](https://img.shields.io/badge/ISO%2026262-ASIL--C%20%2F%20ASIL--D%20Mutation%20Gate-red.svg)](https://www.iso.org/standard/68383.html)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph 4-Critic](https://img.shields.io/badge/LangGraph-4--Critic%20Self--Healing-00A67E.svg)](https://www.langchain.com/langgraph)
[![Ollama Local LLM](https://img.shields.io/badge/LLM-Qwen2.5--Coder%207B-orange.svg)](https://ollama.com/)
[![Streamlit UI](https://img.shields.io/badge/Streamlit-Interactive%20Control%20Center-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker Containerized](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

An enterprise-grade, hybrid **Deterministic + Agentic Software Verification & Validation (V&V) Platform** built with **LangGraph**, **AST Static Analysis**, **Pydantic**, **PyTest**, and **Local LLMs (`Qwen2.5-Coder`)**.

Standard LLM test generators fail in safety-critical and regulated software engineering because they hallucinate decimal boundary math, invent non-existent API methods, or omit required assertions. This platform solves that by combining:
1. **Pydantic Input-Quality Gate (`src/requirement_schema.py`)**
2. **Deterministic Boundary Value Analysis (BVA) & Stateful Multi-Cycle Debounce Engine (`src/bva_engine.py`)**
3. **Zero-Hardcoding AST Code-Context Retriever (`src/code_context_retriever.py`)**
4. **ASPICE SUP.10 Field-Level Diff & SHA-256 Incremental Cache (`verification_state.json`)**
5. **4-Critic Self-Healing LangGraph Workflow (`src/run_pipeline.py`)** with live runtime PyTest traceback recovery
6. **ISO 26262 Fault-Injection Mutation Testing Gate (`src/mutation_coverage_engine.py`)**
7. **Interactive Streamlit Web Control Center (`app.py`)**

---

## 🌐 Cross-Industry Applicability (Enterprise AI, EnergyTech, FinTech & Regulated SaaS)

While demonstrated on an **Electric Vehicle (EV) Battery Management System (BMS) ECU** under **ASPICE SWE.4 / SUP.10** and **ISO 26262**, the underlying verification engine is 100% domain-agnostic and directly applicable to:
* **EnergyTech & Smart Grid Storage (BESS):** High-voltage battery storage, inverter telemetry, and industrial IoT state machines.
* **Enterprise AI & Applied GenAI Engineering:** Zero-hallucination code generation using AST contract extraction, multi-critic guardrails, and GDPR-compliant local LLMs (`Ollama`).
* **FinTech, InsurTech & Enterprise SaaS:** Automated business-rule boundary verification, mutation testing, and audit-ready regulatory compliance reporting (DORA, SOC2, BaFin).
* **MedTech & Aerospace (IEC 62304 / DO-178C):** Bidirectional requirement-to-test traceability and deterministic change impact analysis.

---

## 🏛️ End-to-End System Architecture

```text
  [1. REQUIREMENTS SSOT] (aspice_requirements.json)
   Structured safety & business rules (Thresholds, ASIL ratings, nominal/fault scenarios)
               │
               ▼
  [2. INPUT QUALITY GATE] (src/requirement_schema.py - Pydantic v2)
   Validates requirement IDs, ASIL levels, threshold operators, and scenario schemas
               │
               ▼
  [3. DYNAMIC AST CODE-CONTEXT RETRIEVER] (src/code_context_retriever.py)
   Parses src/bms_ecu.py via Python `ast` to extract live class names, public methods,
   verifiable attributes, valid states, and fault codes (Zero prompt hardcoding!)
               │
               ▼
  [4. DETERMINISTIC MATH & STATEFUL ENGINE] (src/bva_engine.py + Pipeline Enricher)
   Python mathematically computes & injects:
   ├── Boundary Value Analysis (BVA): (Threshold - Step), (Exact Threshold), (Threshold + Step)
   └── Stateful Multi-Cycle Sequences: 1-Cycle Spike Tolerance, 2-Cycle Debounce Trip, & ECU Reset Recovery
               │
               ▼
  [5. SUP.10 CHANGE IMPACT & SHA-256 CACHE] (verification_state.json)
   Compares canonical SHA-256 digest & field-level snapshot (Requirement + AST Contract):
   ├── 🟢 UNCHANGED ──► Reuses existing verified PyTest file in milliseconds
   └── 🟠 MODIFIED / 🔵 NEW ──► Logs exact field deltas & triggers 4-Critic LangGraph Loop:
               │
               ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────┐
  │                   6. LANGGRAPH 4-CRITIC SELF-HEALING WORKFLOW                        │
  │                                                                                      │
  │   ┌──────────────────────────────────────────────────────────────────────────────┐   │
  │   │ [Generator Node] (ChatOllama: qwen2.5-coder:7b @ temperature=0)              │   │
  │   │ Synthesizes @pytest.mark.parametrize suite from BVA matrix + AST Contract    │   │
  │   └──────────────────────────────────────┬───────────────────────────────────────┘   │
  │                                          │                                           │
  │        ┌───────────────────────┬─────────┴─────────────┬───────────────────────┐     │
  │        ▼                       ▼                       ▼                       ▼     │
  │  ┌───────────┐          ┌─────────────┐         ┌─────────────┐        ┌───────────┐ │
  │  │ Critic 1: │          │  Critic 2:  │         │  Critic 3:  │        │ Critic 4: │ │
  │  │  SWE.4    │          │ AST & API   │         │ ISO 26262   │        │  Runtime  │ │
  │  │Traceabil. │          │  Contract   │         │   Safety    │        │  PyTest   │ │
  │  │(Markers & │          │(ast.walk    │         │(Assertions  │        │Dry-Run &  │ │
  │  │ Vectors)  │          │ call check) │         │ & Semantic) │        │Traceback  │ │
  │  └─────┬─────┘          └──────┬──────┘         └──────┬──────┘        └─────┬─────┘ │
  │        └───────────────────────┴───────────┬───────────┴─────────────────────┘       │
  │                                            ▼                                         │
  │                              ┌───────────────────────────┐                           │
  │                              │ [4-Critic Aggregator Gate]│                           │
  │                              └─────────────┬─────────────┘                           │
  │                                            │                                         │
  │      ├── Any Critic / Runtime Failed? ─────┴─► Feeds exact critic error or PyTest    │
  │      │                                         traceback to Generator to self-heal   │
  │      │                                         (or applies SWE.4 Fallback Template)  │
  │      └── All 4 Critics Approved! ────────────► Saves verified tests/test_*.py        │
  └───────────────────────────────────────────────────────────┬──────────────────────────┘
                                                              │
                                                              ▼
  [7. DETERMINISTIC PYTEST & ISO 26262 MUTATION GATE] (src/mutation_coverage_engine.py)
   ├── Executes all 26+ BVA & stateful multi-cycle scenarios against BatteryManagementECU
   ├── Measures ECU Safety Branch Coverage (100%) & Statement Coverage
   └── Injects 4 ECU Code Mutants (MUT-01..MUT-04) to verify 100% Mutation Kill Score
                                                              │
                                                              ▼
  [8. PARTITIONED QA & COMPLIANCE ARTIFACTS] (reports/ & Streamlit UI)
   ├── Passed / Failed HTML Suites: reports/passed/ & reports/failed/
   ├── SUP.10 Change Impact Report: reports/compliance/change_impact_report_<TIMESTAMP>.md
   ├── Bidirectional Traceability Matrix: reports/compliance/traceability_matrix.json
   ├── Interactive HTML Dashboard: reports/compliance/aspice_compliance_report_<TIMESTAMP>.html
   └── Executive Markdown Summary: reports/ai_audit_summary.md
```

---

## 🚀 Key Engineering Innovations

### 1. 8-Layer Defense-in-Depth Against LLM Hallucinations
1. **Zero-Temperature Greedy Decoding:** Runs `ChatOllama(model="qwen2.5-coder:7b", temperature=0)` for deterministic code synthesis.
2. **Pydantic Input-Quality Gate (`src/requirement_schema.py`):** Blocks malformed requirements before any LLM invocation.
3. **AST-Based Dynamic Code-Context Retriever (`src/code_context_retriever.py`):** Dynamically parses `src/bms_ecu.py` into an Abstract Syntax Tree (`ast.parse`) to extract public methods, attributes, valid states, and fault codes—eliminating hardcoded prompt assumptions.
4. **Deterministic Boundary Math (`src/bva_engine.py`):** Python calculates exact test vectors (`threshold - step`, `threshold`, `threshold + step`) at `0.1 °C` and `0.01 V` (`10 mV`) precision along with ground-truth expected states (`NORMAL` vs `FAULT_SHUTDOWN`).
5. **Stateful Multi-Cycle Debounce & Reset Sequences:** Injects multi-step timeline vectors (`"sequence"`) verifying that 1-cycle voltage spikes (`4.30 V`) are tolerated (`debounce_counter == 1`), 2 consecutive cycles latch `FAULT_SHUTDOWN`, and `reset_ecu()` restores normal operation.
6. **4-Critic Self-Healing LangGraph Gate:**
   * **Critic 1 (`traceability_critic_node`):** Verifies `@pytest.mark.requirement("<REQ_ID>")`, `@pytest.mark.parametrize`, and 100% scenario vector inclusion.
   * **Critic 2 (`api_syntax_critic_node`):** Walks the Python AST (`ast.walk`) to verify valid syntax and enforce calls strictly against the live AST-extracted ECU contract.
   * **Critic 3 (`safety_critic_node`):** Verifies explicit assertions on `ecu.state`, `ecu.contactor_closed`, and `ecu.fault_code` via AST + semantic review.
   * **Critic 4 (`runtime_execution_critic_node`):** Executes a live `pytest --tb=short` dry-run inside the LangGraph loop and feeds runtime tracebacks back to the Generator Agent for automatic self-healing (ASPICE SUP.9).
7. **Deterministic SWE.4 Fallback Template (`build_fallback_test_code`):** Guarantees 100% valid, executable test output even if retries are exhausted or when running in cloud CI without a local GPU/Ollama instance.
8. **ISO 26262 Fault-Injection Mutation Gate (`src/mutation_coverage_engine.py`):** Injects 4 synthetic bugs (`MUT-01` to `MUT-04`) into `bms_ecu.py` (boundary shifts, relational flips, fault masking) and verifies that the generated PyTest suite catches and kills 100% of mutants.

### 2. ASPICE SUP.10 Change Impact & Field-Level Diff Engine
* Stores a structured baseline snapshot of every requirement and the AST-extracted ECU contract inside `verification_state.json`.
* Automatically classifies every requirement on each run as 🔵 **`NEW`**, 🟠 **`MODIFIED`** (listing exact field-level deltas like ``Threshold Value: `60.0` -> `62.0` ``), or 🟢 **`UNCHANGED (Cached)`**.

---

## 🛠️ Tech Stack & Standards

| Domain | Technologies / Standards |
| :--- | :--- |
| **Engineering Standards** | ASPICE v3.1 (SYS.2, SWE.4, SYS.5, SUP.9, SUP.10), ISO 26262 Part 6 (ASIL-C / ASIL-D) |
| **Agentic Orchestration** | LangGraph (`StateGraph`), LangChain (`langchain-ollama`) |
| **Local LLM Inference** | Ollama (`qwen2.5-coder:7b`, `temperature=0`) with Cloud CI Fallback |
| **Static Analysis & Math** | Python `ast` (Dynamic Code RAG & Call Inspector), Pydantic v2, Deterministic BVA Engine |
| **Verification & Mutation** | PyTest, `pytest-html`, Custom ISO 26262 Fault-Injection Mutation Engine |
| **Interactive Web UI** | Streamlit (`app.py` Live Control Center) |
| **DevOps & CI/CD** | Python 3.11+, Docker, Docker Compose, GitHub Actions (`ubuntu-latest`) |

---

## 📂 Project Structure

```text
BMS-ECU-Pipeline/
├── .github/
│   └── workflows/
│       └── pipeline.yml                     # Cloud-native GitHub Actions CI/CD workflow
├── reports/
│   ├── passed/                              # Partitioned HTML reports for passing test suites
│   ├── failed/                              # Partitioned HTML reports for failing test suites
│   ├── compliance/
│   │   ├── aspice_compliance_report_*.html  # Interactive SWE.4, SUP.10 & Mutation HTML Dashboard
│   │   ├── change_impact_report_*.md        # SUP.10 Requirement Change Impact & Field Delta log
│   │   └── traceability_matrix.json         # Bidirectional traceability, coverage & mutation JSON
│   └── ai_audit_summary.md                  # Executive Markdown audit summary
├── src/
│   ├── bms_ecu.py                           # Simulated BMS ECU State Machine (BVA + Debounce + Reset)
│   ├── bva_engine.py                        # Deterministic Boundary Value Analysis (BVA) math engine
│   ├── code_context_retriever.py            # Phase 3A: AST-based dynamic ECU contract retriever
│   ├── mutation_coverage_engine.py          # Phase 3B: ISO 26262 branch coverage & mutation engine
│   ├── requirement_schema.py                # Pydantic input-quality gate schema definitions
│   ├── generate_audit_report.py             # HTML Compliance Dashboard generator (SWE.4 + SUP.10 + Mutation)
│   ├── ollama_auditor.py                    # AI executive audit summary generator
│   └── run_pipeline.py                      # Main 4-Critic Self-Healing Orchestrator & Test Runner
├── tests/                                   # Auto-generated parameterized PyTest suites (test_sys_2_bms_*.py)
├── app.py                                   # Phase 5: Interactive Streamlit Web Control Center
├── aspice_requirements.json                 # Single Source of Truth (SSOT) for BMS safety requirements
├── verification_state.json                  # SHA-256 incremental manifest cache & SUP.10 snapshots
├── pytest.ini                               # PyTest configuration & custom ASPICE marker registration
├── Dockerfile                               # Production Python 3.11 container specification
├── docker-compose.yml                       # Container orchestration with host Ollama bridge
├── requirements.txt                         # Locked Python dependencies
└── README.md                                # Project documentation
```

---

## 📋 ISO 26262 & ASPICE SWE.4 Safety Verification Matrix

| Requirement ID | Module / Safety Title | ASIL | Target Metric & Rule | BVA & Stateful Vectors Verified | Expected ECU Fault State & Code |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **SYS.2-BMS-001** | Cell Over-Temperature Isolation | **ASIL-D** | `temperature > 60.0 °C` | Nominal, Fault, BVA (`59.9°C`, `60.0°C`, `60.1°C`), Fault $\rightarrow$ `reset_ecu()` $\rightarrow$ Normal Recovery | `FAULT_SHUTDOWN` (`contactor=False`)<br>`ERR_OVERTEMP_CRITICAL` |
| **SYS.2-BMS-002** | Cell Over-Voltage Protection (2-Cycle Debounce) | **ASIL-C** | `voltage > 4.25 V` | Nominal, Fault, BVA (`4.24V`, `4.25V`, `4.26V`), 1-Cycle Spike Tolerated, Transient Spike Recovery, 2-Cycle Consecutive Trip, Fault $\rightarrow$ Reset Recovery | `FAULT_SHUTDOWN` (`contactor=False`)<br>`ERR_OVERVOLTAGE` |
| **SYS.2-BMS-003** | Cell Under-Voltage Protection | **ASIL-D** | `voltage < 2.50 V` | Nominal, Fault, BVA (`2.49V`, `2.50V`, `2.51V`) | `FAULT_SHUTDOWN` (`contactor=False`)<br>`ERR_UNDERVOLTAGE` |
| **SYS.2-BMS-004** | Thermal Runaway Mitigation under CAN Loss | **ASIL-D** | `temperature > 65.0 °C` **AND** `can_active == False` | Nominal (`45°C`, CAN=True), High Temp with CAN Active (`66°C`, CAN=True), Critical Thermal + CAN Loss (`66°C`, CAN=False) | `FAULT_SHUTDOWN` (`contactor=False`)<br>`ERR_CRITICAL_THERMAL_CAN_FAULT` |

---

## 🖥️ Quick Start Guide (CLI, Streamlit Web UI & Docker)

### 1. Local Environment Setup
```powershell
git clone https://github.com/PrathameshYawalkar15/BMS-ECU-Pipeline.git
cd BMS-ECU-Pipeline

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install streamlit
```

*(Ensure Ollama is running locally with `ollama pull qwen2.5-coder:7b` for local LLM generation; otherwise the pipeline automatically uses its deterministic SWE.4 fallback generator).*

### 2. Run the Interactive Streamlit Web Control Center (Phase 5)
Launch the visual web interface to inspect requirements, modify thresholds live, trigger the 4-Critic pipeline, and view SUP.10 diffs and mutation scores in your browser:
```powershell
streamlit run app.py
```

### 3. Run the CLI Pipeline Directly
```powershell
# Incremental cached run (only regenerates modified requirements)
python src/run_pipeline.py

# Force fresh full regeneration (clears cache & regenerates all tests)
Remove-Item -Path tests\*.py -Force -ErrorAction SilentlyContinue
Remove-Item -Path verification_state.json -Force -ErrorAction SilentlyContinue
python src/run_pipeline.py
```

### 4. Run via Docker Compose
```powershell
docker compose up --build
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.