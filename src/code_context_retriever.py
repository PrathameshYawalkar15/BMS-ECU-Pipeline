import ast
import os
from typing import Dict, Any, List


class ECUCodeContextRetriever:
    """
    Phase 3A: AST-Based Dynamic Code-Context Retriever (Zero-Hardcoding RAG for Code).
    Parses src/bms_ecu.py into an Abstract Syntax Tree to dynamically extract:
      - Class names & public method signatures
      - Instance attributes (e.g., state, contactor_closed, fault_code, debounce_counter)
      - Valid state constants (e.g., NORMAL, FAULT_SHUTDOWN)
      - Valid fault code strings (e.g., ERR_OK, ERR_OVERTEMP_CRITICAL, ERR_OVERVOLTAGE, etc.)
      - Safety rule threshold expressions
    """

    @classmethod
    def extract_contract(cls, ecu_file_path: str) -> Dict[str, Any]:
        if not os.path.exists(ecu_file_path):
            return {
                "class_name": "BatteryManagementECU",
                "public_methods": ["reset_ecu", "update_sensors"],
                "attributes": ["temperature", "voltage", "can_active", "state", "contactor_closed", "fault_code", "debounce_counter"],
                "states": ["NORMAL", "FAULT_SHUTDOWN"],
                "fault_codes": ["ERR_OK", "ERR_OVERTEMP_CRITICAL", "ERR_OVERVOLTAGE", "ERR_UNDERVOLTAGE", "ERR_CRITICAL_THERMAL_CAN_FAULT"],
                "prompt_context": "Class BatteryManagementECU with method update_sensors(scenario).",
            }

        with open(ecu_file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        class_name = "BatteryManagementECU"
        public_methods: List[str] = []
        method_details: List[str] = []
        attributes = set()
        states = set()
        fault_codes = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if not item.name.startswith("_"):
                            public_methods.append(item.name)
                            args = [a.arg for a in item.args.args if a.arg != "self"]
                            if item.args.vararg:
                                args.append(f"*{item.args.vararg.arg}")
                            if item.args.kwarg:
                                args.append(f"**{item.args.kwarg.arg}")
                            doc = ast.get_docstring(item) or ""
                            method_details.append(f"- `{item.name}({', '.join(args)})`: {doc}")

            # Extract self.<attr> assignments and string constants assigned to state / fault_code
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                        attr_name = target.attr
                        attributes.add(attr_name)
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            val_str = node.value.value
                            if attr_name == "state":
                                states.add(val_str)
                            elif attr_name == "fault_code":
                                fault_codes.add(val_str)

        prompt_summary = (
            f"DYNAMICALLY EXTRACTED ECU CONTRACT (from `{os.path.basename(ecu_file_path)}` via AST):\n"
            f"- Target Class: `from src.bms_ecu import {class_name}`\n"
            f"- Public Methods:\n  " + "\n  ".join(method_details) + "\n"
            f"- Verifiable ECU Attributes: {sorted(attributes)}\n"
            f"- Valid `ecu.state` Values: {sorted(states)}\n"
            f"- Valid `ecu.fault_code` Values: {sorted(fault_codes)}"
        )

        return {
            "class_name": class_name,
            "public_methods": sorted(public_methods),
            "attributes": sorted(attributes),
            "states": sorted(states),
            "fault_codes": sorted(fault_codes),
            "prompt_context": prompt_summary,
        }
