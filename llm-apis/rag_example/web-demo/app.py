from flask import Flask, render_template, request, jsonify
import sys
import os
from pathlib import Path
sys.path.insert(0, "..")

import json
import requests
import chromadb
from dotenv import load_dotenv
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Initialize
env_path = Path("../..") / ".env"
load_dotenv(dotenv_path=env_path)

print("Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("✓ Embedding model loaded")

# Use absolute path to ChromaDB (same as notebook)
chroma_db_path = str(Path(__file__).parent.parent / "chroma_db")
print(f"ChromaDB path: {chroma_db_path}")

chroma_client = chromadb.PersistentClient(path=chroma_db_path)

# Try to get collection, create helpful error if it doesn't exist
try:
    collection = chroma_client.get_collection(name="clean_air_act")
    print("✓ ChromaDB collection loaded successfully")
except Exception as e:
    print("❌ ERROR: ChromaDB collection 'clean_air_act' not found!")
    print("\nYou must run the notebook cells first to create the vector database:")
    print("1. Open compliance_rag_exercise.ipynb")
    print("2. Run cells 1-10 to load PDF and create embeddings")
    print("3. Then start the web server (Cell 21)")
    print(f"\nOriginal error: {e}")
    sys.exit(1)

# Bedrock API configuration
bedrock_api_key = os.getenv("BEDROCK_API_KEY")
aws_region = os.getenv("AWS_REGION", "us-east-1")
bedrock_endpoint = f"https://bedrock-runtime.{aws_region}.amazonaws.com/model/anthropic.claude-3-haiku-20240307-v1:0/invoke"

if not bedrock_api_key:
    print("❌ ERROR: BEDROCK_API_KEY not found!")
    print("Expected file: /Users/troymarrotte/Development/bis-438-genai/llm-apis/.env")
    sys.exit(1)
else:
    print(f"✓ Bedrock API configured ({aws_region})")

def search_and_check(facility_info, n_results=3):
    query_embedding = embedding_model.encode([facility_info]).tolist()
    search_results = collection.query(query_embeddings=query_embedding, n_results=n_results)
    
    context_parts = []
    sources = []
    chunks = []
    for i, (doc, metadata, distance) in enumerate(zip(
        search_results["documents"][0],
        search_results["metadatas"][0],
        search_results["distances"][0]
    ), 1):
        page = metadata.get("page", "N/A")
        context_parts.append(f"[Source {i} - Page {page}]\n{doc}")
        sources.append(f"Page {page}")
        chunks.append({"id": i, "content": doc, "page": page, "distance": distance})
    
    context = "\n\n".join(context_parts)
    
    system_prompt = """You are an environmental compliance expert. Analyze facility emissions against Clean Air Act requirements.

RESPOND ONLY WITH VALID JSON:
{
  "compliance_status": "COMPLIANT" | "NON-COMPLIANT" | "INSUFFICIENT_INFO",
  "reasoning": "Brief explanation with specific citations",
  "relevant_sections": ["List of applicable regulatory sections"],
  "recommendation": "Specific action required or confirmation"
}

Base assessment ONLY on the provided Clean Air Act context."""
    
    user_prompt = f"""Clean Air Act Context:
{context}

---

Facility Report:
{facility_info}

---

Provide compliance assessment as JSON."""
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": user_prompt}],
        "system": system_prompt
    }
    
    headers = {
        "Authorization": f"Bearer {bedrock_api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(bedrock_endpoint, headers=headers, json=request_body)
    
    if response.status_code != 200:
        raise Exception(f"Bedrock API error: {response.status_code} - {response.text}")
    
    response_body = response.json()
    llm_output = response_body["content"][0]["text"]
    
    if "```json" in llm_output:
        llm_output = llm_output.split("```json")[1].split("```")[0].strip()
    elif "```" in llm_output:
        llm_output = llm_output.split("```")[1].split("```")[0].strip()

    # Sanitize: escape control characters that appear literally inside JSON string values.
    # LLMs sometimes emit unescaped newlines/carriage returns inside strings, which
    # causes json.loads to raise JSONDecodeError: Invalid control character.
    sanitized = []
    in_string = False
    escaped = False
    for ch in llm_output:
        if escaped:
            sanitized.append(ch)
            escaped = False
        elif ch == "\\" and in_string:
            sanitized.append(ch)
            escaped = True
        elif ch == '"':
            in_string = not in_string
            sanitized.append(ch)
        elif in_string and ord(ch) < 0x20:
            if ch == "\n":
                sanitized.append("\\n")
            elif ch == "\r":
                sanitized.append("\\r")
            elif ch == "\t":
                sanitized.append("\\t")
            # discard other control characters
        else:
            sanitized.append(ch)
    llm_output = "".join(sanitized)

    result = json.loads(llm_output)
    result["chunks"] = chunks
    result["sources"] = sources
    
    return result

@app.route("/")
def index():
    return render_template("compliance_checker.html")

@app.route("/check", methods=["POST"])
def check():
    data = request.json
    facility_info = data.get("facility_info", "")
    n_results = data.get("n_results", 3)
    
    try:
        result = search_and_check(facility_info, n_results)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)
