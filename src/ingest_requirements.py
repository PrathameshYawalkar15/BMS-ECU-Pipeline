import json
import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

def ingest_requirements():
    # Dynamically find the project root and point to aspice_requirements.json
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "aspice_requirements.json")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Could not find requirements file at {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        requirements = json.load(f)

    documents = []
    for req in requirements:
        params = req.get("parameters", {})
        content = (
            f"Requirement ID: {req.get('req_id')}\n"
            f"Title: {req.get('title')}\n"
            f"ASIL Rating: {req.get('asil')}\n"
            f"Description: {req.get('description')}\n"
            f"Metric: {params.get('metric')}\n"
            f"Threshold Value: {params.get('threshold_value')}\n"
            f"Expected Fault Code: {params.get('expected_fault')}"
        )
        
        metadata = {
            "requirement_id": req.get("req_id"),
            "asil": req.get("asil"),
            "threshold_metric": params.get("metric"),
        }
        
        documents.append(Document(page_content=content, metadata=metadata))

    # Use local Hugging Face embeddings (Runs 100% offline, zero API cost)
    print("Loading local Hugging Face embedding model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    collection_name="aspice_requirements",
    persist_directory=os.path.join(base_dir, "chroma_db")
)

if __name__ == "__main__":
    ingest_requirements()