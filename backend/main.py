
import json
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

from src.ml_model import (
    load_model,
    predict_risk,
    classify_risk,
)

from src.copilot import chat
from src.knowledge import (
    search_knowledge,
    format_context,
    format_references,
)

app = FastAPI(
    title="Paramedic AI API",
    version="1.0.0",
)


# Allow the future website to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():
    return {
        "name": "Paramedic AI",
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# ML ASSESSMENT
# ============================================================

class PatientAssessment(BaseModel):

    age: float
    heart_rate: float
    systolic_bp: float
    diastolic_bp: float
    respiratory_rate: float
    spo2: float
    temperature: float


@app.post("/api/assessment")
def assessment(patient: PatientAssessment):

    model = load_model()

    probability = predict_risk(
        model,
        patient.age,
        patient.heart_rate,
        patient.systolic_bp,
        patient.diastolic_bp,
        patient.respiratory_rate,
        patient.spo2,
        patient.temperature,
    )

    category = classify_risk(
        probability
    )

    return {
        "probability": probability,
        "category": category,
    }

# ============================================================
# PARAMEDIC COPILOT
# ============================================================

class CopilotRequest(BaseModel):
    messages: list[dict]


@app.post("/api/copilot")
def copilot(request: CopilotRequest):

    # Keep only recent conversation history
    recent_messages = request.messages[-6:]

    if not recent_messages:
        return {
            "answer": "Please enter a question.",
            "references": [],
        }

    question = recent_messages[-1]["content"]

    # Search authorized knowledge sources
    results = search_knowledge(
        question,
        top_k=3,
    )

    context = format_context(results)

    # Prevent retrieved documents from becoming too large
    MAX_CONTEXT_CHARS = 6000

    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS]

    # Ask the Copilot
    answer = chat(
        messages=recent_messages,
        context=context,
    )

    # Add references
    references = format_references(results)

    return {
        "answer": answer,
        "references": references,
    }


# ============================================================
# KNOWLEDGE MANAGER
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS_DIR = (
    PROJECT_ROOT
    / "data"
    / "documents"
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
}


@app.post("/api/knowledge/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    filename = file.filename or ""

    extension = Path(
        filename
    ).suffix.lower()


    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed.",
        )


    DOCUMENTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    destination = (
        DOCUMENTS_DIR
        / Path(filename).name
    )


    contents = await file.read()


    destination.write_bytes(
        contents
    )


    return {
        "success": True,
        "filename": destination.name,
        "message": (
            f"Uploaded: {destination.name}"
        ),
    }

# ============================================================
# KNOWLEDGE METADATA
# ============================================================

REGISTRY_PATH = (
    PROJECT_ROOT
    / "data"
    / "knowledge"
    / "sources.json"
)


class SourceMetadata(BaseModel):
    filename: str
    title: str
    jurisdiction: str
    document_type: str
    effective_date: str | None = None
    version: str | None = None
    authority: str = ""
    status: str = "active"
    review_required: bool = True


@app.post("/api/knowledge/metadata")
def save_metadata(
    metadata: SourceMetadata
):

    if not metadata.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )


    registry = {}


    if REGISTRY_PATH.exists():

        try:

            with open(
                REGISTRY_PATH,
                "r",
                encoding="utf-8-sig",
            ) as file:

                registry = json.load(file)

        except json.JSONDecodeError:

            registry = {}


    registry[
        metadata.filename
    ] = {

        "title": metadata.title,

        "jurisdiction":
            metadata.jurisdiction,

        "document_type":
            metadata.document_type,

        "effective_date":
            metadata.effective_date,

        "version":
            metadata.version,

        "authority":
            metadata.authority,

        "status":
            metadata.status,

        "review_required":
            metadata.review_required,
    }


    REGISTRY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    with open(
        REGISTRY_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            registry,
            file,
            indent=2,
        )


    return {
        "success": True,
        "filename": metadata.filename,
        "message": "Metadata saved.",
    }

@app.get("/api/knowledge/sources")
def get_sources():

    registry = {}

    if REGISTRY_PATH.exists():

        try:

            with open(
                REGISTRY_PATH,
                "r",
                encoding="utf-8-sig",
            ) as file:

                registry = json.load(file)

        except json.JSONDecodeError:

            registry = {}


    sources = []

    for filename, metadata in registry.items():

        source = {
            "filename": filename,
            **metadata,
        }

        sources.append(source)


    return {
        "sources": sources
    }


# ============================================================
# KNOWLEDGE INDEX REBUILD
# ============================================================

import subprocess
import sys


@app.post("/api/knowledge/rebuild")
def rebuild_knowledge():

    ingest = subprocess.run(
        [
            sys.executable,
            str(
                PROJECT_ROOT
                / "src"
                / "ingest.py"
            ),
        ],
        capture_output=True,
        text=True,
    )


    if ingest.returncode != 0:

        raise HTTPException(
            status_code=500,
            detail=(
                "Document ingestion failed.\n\n"
                + ingest.stderr
            ),
        )


    build_index = subprocess.run(
        [
            sys.executable,
            str(
                PROJECT_ROOT
                / "src"
                / "build_index.py"
            ),
        ],
        capture_output=True,
        text=True,
    )


    if build_index.returncode != 0:

        raise HTTPException(
            status_code=500,
            detail=(
                "Knowledge index rebuild failed.\n\n"
                + build_index.stderr
            ),
        )


    return {
        "success": True,

        "message":
            "Knowledge index rebuilt successfully.",

        "ingestion_output":
            ingest.stdout,

        "index_output":
            build_index.stdout,
    }

