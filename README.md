\# OCR Evaluation Pipeline



A Python-based evaluation framework for measuring OCR accuracy, field-level correctness, extraction faithfulness, risk, and robustness under controlled image degradation.



The project is designed for document-processing systems where OCR errors can have different levels of impact. Instead of relying only on raw OCR text similarity, it evaluates critical fields and determines whether an extracted document should \*\*PASS, REVIEW, or FAIL\*\*.



\## Features



\* OCR extraction using Tesseract

\* Character Error Rate (CER)

\* Word Error Rate (WER)

\* Field-level accuracy

\* Critical-field validation

\* Extraction faithfulness checks

\* Risk-based PASS / REVIEW / FAIL classification

\* Batch document evaluation

\* Robustness testing under:



&#x20; \* Blur

&#x20; \* Contrast changes

&#x20; \* JPEG compression

&#x20; \* Noise

&#x20; \* Rotation

\* JSON evaluation reports

\* Markdown robustness reports

\* Automated test suite with \*\*59 tests\*\*



\## Evaluation Results



Current controlled robustness evaluation:



| Degradation | Tests | Passed | Failed | Pass Rate | Max Passing Level | First Failure |

| ----------- | ----: | -----: | -----: | --------: | ----------------: | ------------: |

| Blur        |     4 |      3 |      1 |     75.0% |                11 |            15 |

| Contrast    |     4 |      4 |      0 |    100.0% |                 4 |           N/A |

| JPEG        |     4 |      4 |      0 |    100.0% |                50 |           N/A |

| Noise       |     6 |      4 |      2 |     66.7% |                25 |            40 |

| Rotation    |     4 |      2 |      2 |     50.0% |                 5 |            10 |



Overall evaluation:



\* \*\*22 documents evaluated\*\*

\* \*\*17 PASS\*\*

\* \*\*5 FAIL\*\*

\* \*\*0 REVIEW\*\*

\* Average CER: \*\*0.1176\*\*

\* Average WER: \*\*0.1329\*\*

\* Average field accuracy: \*\*83.52%\*\*



These results come from a controlled test dataset and demonstrate the evaluation methodology rather than production OCR accuracy.



\## Architecture



```text

&#x20;                   Input Documents

&#x20;                         │

&#x20;                         ▼

&#x20;                   ┌───────────┐

&#x20;                   │ OCR Engine│

&#x20;                   │ Tesseract │

&#x20;                   └─────┬─────┘

&#x20;                         │

&#x20;                         ▼

&#x20;                Extracted OCR Text

&#x20;                         │

&#x20;                         ▼

&#x20;             ┌──────────────────────┐

&#x20;             │ Document Evaluation  │

&#x20;             └──────────┬───────────┘

&#x20;                        │

&#x20;         ┌──────────────┼──────────────┐

&#x20;         ▼              ▼              ▼

&#x20;      CER / WER    Field Accuracy   Faithfulness

&#x20;         │              │              │

&#x20;         └──────────────┼──────────────┘

&#x20;                        ▼

&#x20;                 Risk Classification

&#x20;                        │

&#x20;               ┌────────┼────────┐

&#x20;               ▼        ▼        ▼

&#x20;              PASS    REVIEW    FAIL

&#x20;                        │

&#x20;                        ▼

&#x20;                   JSON Report

&#x20;                        │

&#x20;                        ▼

&#x20;                Robustness Analysis

&#x20;                        │

&#x20;                        ▼

&#x20;                 Markdown Report

```



\## Project Structure



```text

ocr-evaluation-pipeline/

│

├── data/

│   ├── ground\_truth/

│   ├── sample/

│   └── degraded/

│

├── reports/

│   ├── degraded\_evaluation.json

│   └── robustness\_report.md

│

├── src/

│   ├── evaluation/

│   │   ├── batch\_evaluator.py

│   │   ├── critical\_fields.py

│   │   ├── evaluator.py

│   │   ├── extractor.py

│   │   ├── faithfulness.py

│   │   ├── metrics.py

│   │   ├── risk.py

│   │   └── robustness.py

│   │

│   ├── ocr/

│   │   └── engine.py

│   │

│   ├── reporting/

│   │   └── report\_generator.py

│   │

│   └── evaluate.py

│

├── tests/

│   ├── test\_batch\_evaluator.py

│   ├── test\_critical\_fields.py

│   ├── test\_evaluator.py

│   ├── test\_extractor.py

│   ├── test\_faithfulness.py

│   ├── test\_faithfulness\_edge\_cases.py

│   ├── test\_faithfulness\_field\_aware.py

│   ├── test\_metrics.py

│   ├── test\_ocr.py

│   ├── test\_pipeline.py

│   ├── test\_reporting.py

│   ├── test\_risk.py

│   └── test\_robustness.py

│

├── requirements.txt

├── requirements-dev.txt

└── README.md

```



\## Installation



\### 1. Clone the repository



```bash

git clone <your-repository-url>

cd ocr-evaluation-pipeline

```



\### 2. Create a virtual environment



Windows:



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



Linux/macOS:



```bash

python3 -m venv .venv

source .venv/bin/activate

```



\### 3. Install dependencies



For runtime dependencies:



```bash

pip install -r requirements.txt

```



For development and testing:



```bash

pip install -r requirements-dev.txt

```



\### 4. Install Tesseract OCR



`pytesseract` is a Python wrapper and does not include the Tesseract OCR engine itself.



Install Tesseract separately and verify it is available:



```bash

tesseract --version

```



If Tesseract is not available on your system PATH, configure the executable path before running the pipeline.



\## Dependencies



Runtime dependencies:



\* \*\*Pillow\*\* — image loading and processing

\* \*\*pytesseract\*\* — Python interface to Tesseract OCR

\* \*\*jiwer\*\* — CER/WER calculation

\* \*\*OpenCV\*\* — controlled image degradation generation

\* \*\*NumPy\*\* — image-array operations



Development dependency:



\* \*\*pytest\*\* — automated testing



\## Running Tests



Run the complete test suite:



```bash

python -m pytest -v

```



Current test status:



```text

59 passed

```



The tests cover:



\* OCR extraction

\* Field extraction

\* Field accuracy

\* Critical fields

\* Faithfulness

\* Faithfulness edge cases

\* CER/WER metrics

\* Risk classification

\* Batch evaluation

\* JSON reporting

\* Robustness parsing

\* Robustness reporting

\* Pipeline execution



\## Running the Evaluation



Evaluate the degraded document dataset:



```powershell

python -m src.evaluate `

&#x20;   --documents data/degraded/test\_document `

&#x20;   --ground-truth data/ground\_truth `

&#x20;   --output reports/degraded\_evaluation.json

```



The evaluation produces:



```text

reports/

├── degraded\_evaluation.json

└── robustness\_report.md

```



The JSON report contains document-level evaluation results and aggregate metrics.



The Markdown report summarizes OCR robustness by degradation type.



\## Evaluation Methodology



\### Character Error Rate



CER measures character-level differences between OCR output and reference text.



```text

CER = character errors / reference characters

```



Lower is better.



\### Word Error Rate



WER measures word-level differences between OCR output and reference text.



```text

WER = word errors / reference words

```



Lower is better.



\### Field Accuracy



The pipeline evaluates important document fields instead of relying only on full-text similarity.



Example fields include:



```text

Owner Name

Father Name

Survey Number

Area

Village

Tehsil

District

Registration Number

```



This makes the evaluation more relevant to structured document-processing workflows.



\### Faithfulness



The pipeline verifies that extracted values are actually supported by the OCR output.



An extracted value that is not present in the OCR text is treated as unsupported rather than being considered correct simply because it matches the ground truth.



\### Risk Classification



Not all OCR errors have the same consequences.



The evaluator therefore classifies documents as:



```text

PASS

REVIEW

FAIL

```



Critical-field failures can force a document into `FAIL`, while high-risk non-critical failures can result in `REVIEW`.



\## Robustness Evaluation



The robustness component evaluates OCR performance against controlled image degradations.



Each degradation is represented by a severity level, for example:



```text

blur\_3.png

blur\_7.png

blur\_11.png

blur\_15.png

```



The evaluator reports:



\* Number of tests

\* Number passed

\* Number failed

\* Pass rate

\* Maximum passing severity

\* First failing severity



This provides a simple way to identify where OCR performance begins to degrade.



\## Design Goals



\### 1. Accuracy is not enough



A low CER does not necessarily mean that a document is safe to use. A single incorrect critical field can be more important than many minor OCR errors.



\### 2. OCR output must be faithful



The system should not accept an extracted value simply because it looks plausible. Extracted values should be supported by the OCR output.



\### 3. Robustness should be measurable



OCR systems should be tested under controlled image degradation instead of being evaluated only on clean images.



\## Limitations



This project is an evaluation framework rather than a production OCR service.



Current limitations include:



\* Tesseract is the only OCR engine currently integrated.

\* The test dataset is controlled and relatively small.

\* Evaluation focuses on a predefined set of document fields.

\* Robustness testing uses predefined degradation levels.

\* Production-scale latency and throughput are not currently benchmarked.

\* Multilingual OCR has not been evaluated.



\## Future Improvements



Potential extensions include:



\* Support for multiple OCR engines

\* OCR engine comparison

\* Confidence-score analysis

\* Precision / recall / F1 for field extraction

\* Bounding-box validation

\* Larger real-world document datasets

\* Additional image degradations

\* Performance and latency benchmarking

\* HTML evaluation dashboard

\* CI-based regression testing

\* Automatic robustness threshold detection



\## License



This project is intended as a technical evaluation and portfolio project.



