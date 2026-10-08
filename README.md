# Autonomous ASPICE-Compliant QA Pipeline for EV Battery Management Systems (BMS)

[![ASPICE v3.1 Compliant](https://img.shields.io/badge/ASPICE-SYS.2%20%7C%20SWE.4-blue.svg)](https://www.automotive-spice.com/)
[![Functional Safety](https://img.shields.io/badge/ISO%2026262-ASIL--D%20Ready-red.svg)](https://www.iso.org/standard/68383.html)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Docker Containerized](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI/CD Pipeline](https://img.shields.io/badge/GitHub%20Actions-Automated-2088FF.svg?logo=github-actions&logoColor=white)](https://github.com/)

An enterprise-grade, agentic verification pipeline designed for **Automotive SPICE (ASPICE v3.1)** software quality assurance in Electric Vehicle (EV) Battery Management Systems (BMS). 

This platform replaces brittle, manual test generation with a **Deterministic Agentic RAG Framework (LangGraph + ChromaDB)** that dynamically parses system requirement specifications (SYS.2), synthesizes compliant PyTest verification suites, executes tests against simulated hardware-in-the-loop (HIL) state machines, and enforces a safety-critical **Circuit Breaker** to prevent non-deterministic code execution.

---

## 🏛️ System Architecture

The pipeline follows the classic Automotive **V-Model**, bridging **SYS.2 System Requirements Analysis** directly to **SYS.5 System Integration and Verification Testing** with total bi-directional traceability.

```
       ASPICE SYS.2 Requirements (JSON / Vector Store)
                          │
                          ▼
            [ LangGraph Agentic Orchestrator ]
            ├── Tool 1: ChromaDB RAG Vector Store
            └── Tool 2: Code Validator & PyTest Runner
                          │
                          ▼
             [ Safety Circuit Breaker ]
            ├── System Error / AST Guard Violation -> Immediate Halt
            └── Functional Test Assertion Failure  -> Non-blocking Log
                          │
                          ▼
      [ Hardware Simulation & Partitioned QA Reporting ]
            ├── Passed Tests Report (reports/passed_report.html)
            └── Failed Tests Report (reports/failed_report.html)
```

### Key Engineering Features

* **Dynamic Vector Discovery (ChromaDB):** Replaces static test scripts with dynamic vector indexing. Requirements are ingested, hashed (`MD5`), and indexed to allow runtime discovery and zero-hardcoding batch runs.
* **Safety Circuit Breaker Pattern:** Implements a two-tiered fault architecture:
  1. **System & Security Violations** (e.g., AST guardrail breaches, illegal file inspection, syntax errors) trigger an immediate pipeline abort to guarantee safety compliance.
  2. **Functional Test Assertions** (e.g., ECU fault code mismatches) are safely isolated into dedicated failure logs without disrupting full regression suite completion.
* **Bifurcated QA Reporting:** Automatically parses execution outputs into partitioned, self-contained HTML reports (`passed_report_<TIMESTAMP>.html` and `failed_report_<TIMESTAMP>.html`) for rapid root-cause analysis by QA engineers.
* **Containerized Execution & CI/CD Ready:** Fully dockerized with multi-stage builds and CLI overrides (`--reqs`) for integration into GitHub Actions or GitLab CI runners.

---

## 🛠️ Tech Stack & Standards

| Domain | Technologies / Standards |
| :--- | :--- |
| **Industry Standards** | ASPICE v3.1 (SYS.2 / SYS.5), ISO 26262 (ASIL-B to ASIL-D) |
| **Agentic Framework** | LangGraph, LangChain, OpenRouter API (LLM Integration) |
| **Vector Store / RAG** | ChromaDB (Persistent Embeddings & Parameter Retrieval) |
| **Testing & Verification** | PyTest, PyTest-HTML, Subprocess Execution Isolation |
| **DevOps & Containerization** | Docker, Docker Compose, GitHub Actions, Python 3.11 |

---

## 📂 Project Structure

```text
├── .github/
│   └── workflows/
│       └── pipeline.yml           # CI/CD automated build & verification pipeline
├── config/
│   └── aspice_requirements.json   # Single Source of Truth (SSOT) for safety requirements
├── reports/                       # Generated partitioned HTML test reports
├── src/
│   ├── agent_graph.py             # LangGraph orchestrator & Safety Circuit Breaker
│   ├── bms_ecu.py                 # Simulated BMS Hardware/Software State Machine
│   └── ingest_requirements.py    # Vector store ingestion & hashing engine
├── tests/                         # Auto-generated persistent PyTest verification assets
├── Dockerfile                     # Production container spec
├── docker-compose.yml             # Container orchestration
├── requirements.txt               # Locked project dependencies
└── README.md                      # Project documentation
```

---

## 🚦 Quick Start Guide

### Prerequisites

* Python `3.11+`
* Docker & Docker Compose (Optional, for containerized execution)
* OpenRouter API Key (Set in `.env`)

### 1. Local Environment Setup

Clone the repository and prepare the virtual environment:

```bash
# Clone repository
git clone https://github.com/your-username/BMS-ECU-Pipeline.git
cd BMS-ECU-Pipeline

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
echo "OPENROUTER_API_KEY=your_openrouter_api_key_here" > .env
```

### 2. Requirement Vector Ingestion (ChromaDB)

Ingest ASPICE requirements into the ChromaDB vector database:

```bash
python src/ingest_requirements.py
```

### 3. Pipeline Execution Modes

#### Full Dynamic Batch Run (All Requirements in Vector Store)
```bash
python src/agent_graph.py
```

#### Targeted CLI Execution (Specific Requirement Subset)
```bash
python src/agent_graph.py --reqs SYS.2-BMS-001 SYS.2-BMS-002
```

---

## 🐳 Docker Containerized Execution

Run the complete pipeline inside an isolated Linux container:

```bash
# Build and run default dynamic pipeline
docker compose up --build

# Run targeted requirement verification via Docker
docker compose run app python src/agent_graph.py --reqs SYS.2-BMS-001
```

---

## 📊 Automated QA Reports

Following every execution, generated test artifacts are written to `tests/` (e.g., `tests/test_sys_2_bms_001.py`) and partitioned reports are compiled into `reports/`:

* **Passed Suite:** `reports/passed_report_<TIMESTAMP>.html` — Full audit trail for compliance verification.
* **Failed Suite:** `reports/failed_report_<TIMESTAMP>.html` — Isolated assertion logs, telemetry data, and stack traces for engineering defect resolution.

---

## 📋 ISO 26262 Safety Verification Matrix

| Requirement ID | Module / Title | ASIL | Target Metric | Threshold | Expected ECU Fault Code |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **SYS.2-BMS-001** | Cell Over-Temperature Isolation | **ASIL-D** | Temperature | `> 60.0 °C` | `ERR_OVERTEMP_CRITICAL` |
| **SYS.2-BMS-002** | Cell Over-Voltage Protection | **ASIL-C** | Voltage | `> 4.25 V` | `ERR_OVERVOLTAGE` |
| **SYS.2-BMS-003** | Cell Under-Voltage Protection | **ASIL-D** | Voltage | `< 2.50 V` | `ERR_UNDERVOLTAGE` |

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.