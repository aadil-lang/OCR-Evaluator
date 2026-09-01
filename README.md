# OCR Evaluation & Robustness Testing Platform

> An engineering-focused document intelligence platform for evaluating OCR accuracy, field-level correctness, confidence, and robustness before extracted data is used downstream.

[![Tests](https://img.shields.io/badge/tests-134%20passed-brightgreen)](#testing)
[![Python](https://img.shields.io/badge/python-3.12-blue)](#tech-stack)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](#architecture)
[![React](https://img.shields.io/badge/frontend-React-61DAFB)](#architecture)
[![OCR](https://img.shields.io/badge/OCR-Tesseract-orange)](#tech-stack)

## Overview

OCR systems are often evaluated using a single accuracy number. That is not enough for document-processing systems where a small error in a critical field can be more important than several harmless character errors.

This project implements an **OCR evaluation and robustness platform** that evaluates scanned documents at multiple levels:

* Character-level accuracy using CER
* Word-level accuracy using WER
* Field-level exact matching
* Critical-field accuracy
* OCR confidence analysis
* Faithfulness checks
* Risk classification
* PASS / REVIEW / FAIL operational status
* Robustness testing under controlled image degradation
* Automated regression testing
* Interactive React dashboard

The goal is not simply to extract text.

The goal is to answer:

> **"Can this OCR result be trusted?"**

---

# Real-World Applications

This evaluation framework is designed for document-processing systems where OCR errors can have different levels of business impact.

Potential applications include:

- **Land and property records** — validating survey numbers, registration numbers, ownership details, and area measurements.
- **Legal document processing** — identifying extraction mismatches in contracts, deeds, and official records.
- **Banking and financial documents** — validating account numbers, amounts, dates, and customer information.
- **Insurance documents** — evaluating extraction from claims, forms, and supporting documents.
- **Government digitization** — assessing OCR quality when converting scanned records into structured digital data.
- **Enterprise document automation** — determining whether extracted information can safely move to downstream systems or should be sent for human review.

The key production use case is not simply:

> "Did OCR extract the document?"

It is:

> **"Can this extracted information be trusted for the next step?"**

For example, an OCR system may correctly extract 99% of a document while changing a single critical value such as a survey number, policy number, account number, or registration number. A reliability layer should detect that distinction and route the document to `PASS`, `REVIEW`, or `FAIL`.

## Why this project?

Consider a scanned land record containing:

```text
Owner Name: Daniel James Anderson
Survey Number: 128/3
Area: 0.2450 Hectare
Registration Number: REG-2026-001
```

An OCR engine might achieve a high overall text accuracy while incorrectly extracting:

```text
Survey Number: 128/8
```

For a document-processing system, that is potentially a critical failure.

Therefore, this project separates:

### Extraction accuracy

Did the OCR output match the expected ground truth?

### Operational status

Should the result be:

* **PASS** — safe according to the configured evaluation rules
* **REVIEW** — extraction may be accurate, but confidence/risk requires human review
* **FAIL** — a critical extraction failure was detected

This separation is a core design decision throughout the system.

---

# Architecture

```text
                         ┌─────────────────────┐
                         │    React Frontend   │
                         │                     │
                         │ Upload / Results /  │
                         │ Confidence / Risk  │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI API     │
                         │                     │
                         │ /health             │
                         │ /evaluate           │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    OCR Evaluation   │
                         │      Pipeline       │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
              OCR Engine        Extraction       Evaluation
              Tesseract         & Fields         & Metrics
                    │               │                │
                    └───────────────┼────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Risk / Confidence   │
                         │     Assessment      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         PASS / REVIEW / FAIL
```

---

# Evaluation Pipeline

The evaluation flow is:

```text
Document
   │
   ▼
OCR Engine
   │
   ├── OCR text
   └── word-level confidence
   │
   ▼
Field Extraction
   │
   ▼
Ground Truth Comparison
   │
   ├── CER
   ├── WER
   ├── Field Accuracy
   └── Critical Field Accuracy
   │
   ▼
Confidence + Faithfulness + Risk Analysis
   │
   ▼
Operational Status
   │
   ├── PASS
   ├── REVIEW
   └── FAIL
```

---

# Repository Structure

```text
ocr-evaluation-pipeline/
├── src/
│   ├── api.py                 # FastAPI app (health + evaluate endpoints)
│   ├── evaluate.py            # Batch evaluation CLI
│   ├── evaluation/            # Shared field schema, metrics, risk, confidence,
│   │                          #   extraction, faithfulness, robustness logic
│   ├── ocr/                   # Tesseract OCR engine wrapper
│   └── reporting/             # JSON + Markdown report generators
├── frontend/                  # React + Vite evaluation dashboard
├── tests/                     # 134 automated tests
├── data/
│   ├── documents/             # Source document images
│   ├── ground_truth/          # Ground-truth JSON files
│   └── robustness/            # Controlled degradation images + manifest
├── reports/                   # Generated JSON + Markdown reports
├── run_robustness.py          # Robustness evaluation CLI
├── create_degraded_dataset.py # Regenerates the degradation dataset
├── run_pipeline.py            # Batch evaluation entry point
└── requirements.txt
```

---

# Robustness Evaluation

A major part of the project is testing OCR behavior when document quality deteriorates.

The system evaluates controlled degradation across:

* Blur
* Noise
* JPEG compression
* Rotation
* Contrast changes

Rather than simply reporting whether OCR works, the robustness evaluator identifies:

* Accuracy at each severity
* Maximum tested severity that remained accurate
* First severity where extraction became inaccurate
* CER/WER degradation
* Field-level accuracy
* Critical-field accuracy
* Confidence changes
* Operational status

## Current robustness results

| Degradation | Tests | Accurate | Accuracy | Max Accurate Level | First Accuracy Failure |
| ----------- | ----: | -------: | -------: | -----------------: | ---------------------: |
| Blur        |     4 |        4 |     100% |                 15 |                      — |
| Noise       |     4 |        3 |      75% |                 40 |                     60 |
| JPEG        |     4 |        4 |     100% |                 50 |                      — |
| Rotation    |     4 |        1 |      25% |                  2 |                      5 |
| Contrast    |     4 |        4 |     100% |                  4 |                      — |

These results demonstrate an important property of the system: **robustness is measured as a function of degradation severity rather than treated as a binary capability.**

---

# Frontend

The React interface provides an interactive evaluation workflow.

### Upload

Users can:

* Drag and drop a document
* Select PNG/JPEG files
* Preview the source document
* Start an evaluation

### Evaluation dashboard

The results interface displays:

* Overall status
* OCR confidence
* Field accuracy
* Critical-field accuracy
* CER
* WER
* Number of evaluated fields
* Risk signals
* Field-level confidence
* Extraction mismatches
* Raw OCR text

Example status behavior:

```text
PASS
└── Automated evaluation passed

REVIEW
├── Extraction may be accurate
└── Human review recommended

FAIL
├── Critical extraction failure
└── Failed fields displayed
```

---

# Risk-Aware Field Evaluation

Each extracted field is evaluated independently.

Example:

```text
Owner Name
Daniel James Anderson
Confidence: 96.2%
Status: HIGH

Survey Number
128/8
Confidence: 91.4%
Status: FAILED
Reason: FIELD_MISMATCH

Registration Number
REG-2026-001
Confidence: 54.7%
Status: LOW CONFIDENCE
```

This allows the system to distinguish between:

> "The OCR engine produced text."

and:

> "The extracted information is reliable enough for downstream use."

---

# Testing

The project currently contains:

## 134 automated tests

```text
134 passed
0 failed
```

Tests cover areas including:

* OCR extraction
* Field extraction
* Evaluation logic
* Critical fields
* Confidence analysis
* Faithfulness
* Risk classification
* CER/WER metrics
* Robustness evaluation
* API behavior
* Error handling
* Batch evaluation
* Regression scenarios

The test suite was executed twice during final validation with:

```text
134/134 passed
```

---

# End-to-End Validation

The final system was validated using the actual stack:

```text
React
   ↓
FastAPI
   ↓
OCR Evaluation Pipeline
   ↓
Tesseract
```

The following scenarios were tested through the actual browser UI:

| Scenario                   | Result                    |
| -------------------------- | ------------------------- |
| Accurate document          | PASS rendered correctly   |
| Low-confidence document    | REVIEW + risk signal      |
| Inaccurate document        | FAIL + failed field       |
| Missing ground truth       | HTTP 404 + frontend error |
| Invalid upload             | HTTP 400                  |
| Frontend JavaScript errors | 0                         |
| UI assertions              | 20/20 passed              |

The FAIL scenario is particularly important because it previously exposed a frontend/API schema mismatch. The final implementation validates that failed fields can travel from the backend to the UI without crashing the application.

---

# API

## Health

```http
GET /health
```

Example:

```json
{
  "status": "healthy"
}
```

## Evaluate document

```http
POST /evaluate
Content-Type: multipart/form-data
```

The response contains:

```json
{
  "document": "...",
  "status": "REVIEW",
  "summary": {
    "confidence": 90.5,
    "cer": 0.0,
    "wer": 0.0,
    "field_accuracy": 1.0,
    "critical_field_accuracy": 1.0
  },
  "fields": {},
  "risk": {},
  "ocr_text": "..."
}
```

---

# Error Handling

The API explicitly distinguishes different failure conditions.

Examples:

```text
400 → invalid upload
404 → missing ground truth
422 → invalid request
500 → unexpected server failure
```

Batch evaluation also isolates individual document failures so that one corrupt document does not terminate an entire evaluation run.

---

# Tech Stack

### Backend

* Python
* FastAPI
* Tesseract OCR via pytesseract
* Pillow
* pytest

### Dataset generation

* OpenCV
* NumPy

### Frontend

* React
* Vite
* JavaScript
* CSS

### Evaluation

* CER
* WER
* Field-level exact matching
* Confidence analysis
* Critical-field evaluation
* Robustness testing

### Engineering

* Automated testing
* REST API
* CORS
* Temporary file processing
* Structured evaluation reports
* JSON/Markdown reporting

---

# Running Locally

## 1. Clone

```bash
git clone <YOUR_REPOSITORY_URL>
cd ocr-evaluation-pipeline
```

## 2. Create Python environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

Tesseract OCR must also be installed and available on the system PATH.

Verify:

```bash
tesseract --version
```

## 4. Run tests

```bash
pytest
```

Expected:

```text
134 passed
```

## 5. Start the API

```bash
uvicorn src.api:app --host 127.0.0.1 --port 8000
```

API:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 6. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open the Vite URL shown in the terminal.

---

# Running Robustness Evaluation

The controlled degradation dataset (images + manifest) is stored in the repository. To regenerate it from the source document before running the evaluation:

```bash
python create_degraded_dataset.py
```

Then run the robustness evaluation:

```bash
python run_robustness.py `
  --manifest data/robustness/manifest.json `
  --images data/robustness/images `
  --ground-truth data/ground_truth `
  --output reports/robustness_results.json
```

The pipeline generates:

```text
reports/
├── robustness_results.json
└── robustness_results.md
```

---

# Engineering Decisions

Several design decisions were intentionally made to make the system reliable rather than merely functional.

### Accuracy vs operational status

A completely accurate OCR result can still require human review if confidence or risk rules indicate uncertainty.

### Critical fields

Not all document fields have equal importance. Critical fields therefore receive separate evaluation.

### Robustness thresholds

The system records the first degradation severity where accuracy fails instead of reporting only an aggregate score.

### API/UI contract

The backend exposes a structured schema consumed by the frontend so field-level evaluation and risk information remain consistent across layers.

### Regression testing

The project uses automated tests to protect evaluation logic from changes in OCR, extraction, and risk rules.

---

# Known Limitation

The demo API currently evaluates uploaded documents against the project's configured sample ground-truth dataset.

For a production deployment, this would be replaced with document-specific ground-truth selection or a dataset/document identifier.

This limitation is intentional for the current evaluation prototype and does not affect the robustness evaluation framework.

---

# Future Improvements

Potential next steps include:

* Multi-document evaluation UI
* PDF input
* Additional OCR engines
* OCR engine comparison
* More document types
* Learned field extraction
* Visual bounding-box inspection
* Human correction workflow
* Evaluation history
* Persistent experiment tracking
* Model benchmarking
* Cloud deployment
* Dataset versioning
* Production authentication and authorization

---

# What this project demonstrates

This project was built to demonstrate practical AI engineering beyond simply calling an OCR model.

It combines:

**AI/ML**

* OCR
* confidence analysis
* document information extraction
* evaluation metrics
* robustness testing

**Backend engineering**

* FastAPI
* API contracts
* error handling
* batch processing
* structured reports

**Software engineering**

* modular architecture
* automated testing
* regression testing
* failure isolation
* reproducible evaluation

**Frontend engineering**

* React
* interactive document evaluation
* field-level visualization
* risk-aware UI

The central engineering principle is:

> **An AI system should not only produce an answer — it should provide evidence about how reliable that answer is.**
