import json
import hashlib
import chromadb

def ingest_requirements(file_path: str = "aspice_requirements.json", db_path: str = "./bms_vector_store"):
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(
        name="aspice_requirements",
        metadata={"description": "ASPICE SYS.2 Functional Requirements for BMS"}
    )

    with open(file_path, "r") as f:
        requirements = json.load(f)

    for req in requirements:
        req_hash = hashlib.md5(json.dumps(req, sort_keys=True).encode()).hexdigest()
        doc_text = f"{req['req_id']} - {req['title']}: {req['description']}"
        
        collection.upsert(
            ids=[req["req_id"]],
            documents=[doc_text],
            metadatas=[{
                "req_id": req["req_id"],
                "asil": req["asil"],
                "content_hash": req_hash,
                "metric": req["parameters"]["metric"],
                "threshold_value": req["parameters"]["threshold_value"],
                "expected_fault": req["parameters"]["expected_fault"],
                "expected_contactor_state": str(req["parameters"]["expected_contactor_state"])
            }]
        )

    print(f"[ChromaDB] Successfully ingested {len(requirements)} requirements into '{db_path}'.")

if __name__ == "__main__":
    ingest_requirements()