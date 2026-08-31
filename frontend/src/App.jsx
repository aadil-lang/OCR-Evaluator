import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function getConfidenceLevel(confidence) {
  if (confidence >= 80) return "high";
  if (confidence >= 60) return "medium";
  return "low";
}

function getStatusClass(status) {
  return status?.toLowerCase() || "unknown";
}

function formatPercentage(value) {
  if (typeof value !== "number") return "—";
  return `${(value * 100).toFixed(1)}%`;
}

function formatMetric(value) {
  if (typeof value !== "number") return "—";
  return value.toFixed(4);
}

function formatFieldName(fieldName) {
  return fieldName
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function riskFieldNames(entries) {
  if (!Array.isArray(entries)) return [];
  return entries.map((entry) =>
    typeof entry === "string" ? entry : entry?.field
  ).filter(Boolean);
}

function hasRiskField(entries, fieldName) {
  return riskFieldNames(entries).includes(fieldName);
}

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);
  const [showOcrText, setShowOcrText] = useState(false);

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;

    const allowedTypes = [
      "image/png",
      "image/jpeg",
      "image/jpg",
    ];

    if (!allowedTypes.includes(selectedFile.type)) {
      setError("Please upload a PNG or JPEG image.");
      return;
    }

    setFile(selectedFile);
    setResult(null);
    setError(null);
    setShowOcrText(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragActive(false);

    const droppedFile = event.dataTransfer.files?.[0];
    handleFile(droppedFile);
  };

  const handleEvaluate = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/evaluate`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(
          `Evaluation failed with status ${response.status}.`
        );
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message ||
          "Unable to evaluate the document. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const resetEvaluation = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setShowOcrText(false);
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">O</div>

          <div>
            <div className="brand-name">OCR Evaluator</div>

            <div className="brand-subtitle">
              Document Intelligence
            </div>
          </div>
        </div>

        <div className="engine-status">
          <span className="status-dot"></span>
          Evaluation Engine
        </div>
      </header>

      <main className="main">
        {!result && (
          <section className="upload-page">
            <div className="intro">
              <span className="eyebrow">
                DOCUMENT INTELLIGENCE
              </span>

              <h1>
                Evaluate your
                <br />
                <span>document.</span>
              </h1>

              <p>
                Analyze OCR quality, field accuracy, confidence,
                and extraction risk in seconds.
              </p>
            </div>

            <div
              className={`upload-card ${
                dragActive ? "drag-active" : ""
              }`}
              onDragOver={(event) => {
                event.preventDefault();
                setDragActive(true);
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
            >
              <input
                id="file-input"
                type="file"
                accept=".png,.jpg,.jpeg,image/png,image/jpeg"
                hidden
                onChange={(event) =>
                  handleFile(event.target.files?.[0])
                }
              />

              <div className="upload-icon">↑</div>

              <h2>
                {file
                  ? file.name
                  : "Drop your document here"}
              </h2>

              <p>
                {file
                  ? `${(file.size / 1024 / 1024).toFixed(2)} MB`
                  : "or choose an image from your computer"}
              </p>

              <label
                htmlFor="file-input"
                className="choose-button"
              >
                {file
                  ? "Change document"
                  : "Choose document"}
              </label>

              <div className="supported">
                PNG · JPG · JPEG
              </div>
            </div>

            {file && (
              <button
                className="evaluate-button"
                onClick={handleEvaluate}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Evaluating document...
                  </>
                ) : (
                  <>
                    Evaluate document
                    <span>→</span>
                  </>
                )}
              </button>
            )}

            {error && (
              <div className="error-message">
                <strong>Evaluation error</strong>
                <span>{error}</span>
              </div>
            )}

            <div className="privacy-note">
              <span>✓</span>
              Your document is processed by the evaluation
              pipeline and is not stored by the interface.
            </div>
          </section>
        )}

        {result && (
          <section className="results-page">
            <div className="results-header">
              <button
                className="back-button"
                onClick={resetEvaluation}
              >
                ← New evaluation
              </button>

              <div className="document-title">
                <div className="document-icon">▧</div>

                <div>
                  <strong>{result.document}</strong>

                  <span>
                    OCR evaluation result
                  </span>
                </div>
              </div>

              <div
                className={`status-badge ${getStatusClass(
                  result.status
                )}`}
              >
                <span></span>
                {result.status}
              </div>
            </div>

            {/* SUMMARY */}

            <div className="summary-grid">
              <div className="summary-card">
                <span className="summary-label">
                  STATUS
                </span>

                <strong
                  className={`summary-status ${getStatusClass(
                    result.status
                  )}`}
                >
                  {result.status}
                </strong>

                <small>
                  Overall evaluation outcome
                </small>
              </div>

              <div className="summary-card">
                <span className="summary-label">
                  FIELD ACCURACY
                </span>

                <strong>
                  {formatPercentage(
                    result.summary.field_accuracy
                  )}
                </strong>

                <small>
                  Ground-truth field comparison
                </small>
              </div>

              <div className="summary-card">
                <span className="summary-label">
                  CRITICAL ACCURACY
                </span>

                <strong>
                  {formatPercentage(
                    result.summary
                      .critical_field_accuracy
                  )}
                </strong>

                <small>
                  Critical field comparison
                </small>
              </div>

              <div className="summary-card">
                <span className="summary-label">
                  CONFIDENCE
                </span>

                <strong>
                  {result.summary.confidence.toFixed(1)}%
                </strong>

                <small>
                  Average OCR confidence
                </small>
              </div>
            </div>

            <div className="result-grid">
              {/* DOCUMENT */}

              <div className="document-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-eyebrow">
                      SOURCE DOCUMENT
                    </span>

                    <h2>Document</h2>
                  </div>
                </div>

                <div className="document-preview">
                  {file && (
                    <img
                      src={URL.createObjectURL(file)}
                      alt="Uploaded document"
                    />
                  )}
                </div>
              </div>

              {/* EVALUATION */}

              <div className="extraction-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-eyebrow">
                      EVALUATION
                    </span>

                    <h2>Extraction results</h2>
                  </div>
                </div>

                {/* OCR QUALITY */}

                <div className="quality-section">
                  <div className="section-title">
                    <span>OCR QUALITY</span>
                  </div>

                  <div className="metrics-grid">
                    <div className="metric-card">
                      <span>Confidence</span>

                      <strong>
                        {result.summary.confidence.toFixed(
                          1
                        )}
                        %
                      </strong>
                    </div>

                    <div className="metric-card">
                      <span>Field accuracy</span>

                      <strong>
                        {formatPercentage(
                          result.summary.field_accuracy
                        )}
                      </strong>
                    </div>

                    <div className="metric-card">
                      <span>Critical accuracy</span>

                      <strong>
                        {formatPercentage(
                          result.summary
                            .critical_field_accuracy
                        )}
                      </strong>
                    </div>

                    <div className="metric-card">
                      <span>CER</span>

                      <strong>
                        {formatMetric(
                          result.summary.cer
                        )}
                      </strong>

                      <small>
                        Character error rate
                      </small>
                    </div>

                    <div className="metric-card">
                      <span>WER</span>

                      <strong>
                        {formatMetric(
                          result.summary.wer
                        )}
                      </strong>

                      <small>
                        Word error rate
                      </small>
                    </div>

                    <div className="metric-card">
                      <span>Fields</span>

                      <strong>
                        {Object.keys(
                          result.fields || {}
                        ).length}
                      </strong>

                      <small>
                        Evaluated fields
                      </small>
                    </div>
                  </div>
                </div>

                {/* STATUS MESSAGE */}

                {result.status === "REVIEW" && (
                  <div className="review-alert">
                    <div className="alert-icon">!</div>

                    <div>
                      <strong>
                        Human review recommended
                      </strong>

                      <p>
                        The extracted information appears
                        accurate, but one or more fields
                        require additional review because
                        of confidence or risk rules.
                      </p>
                    </div>
                  </div>
                )}

                {result.status === "PASS" && (
                  <div className="success-alert">
                    <div className="alert-icon">✓</div>

                    <div>
                      <strong>
                        Evaluation passed
                      </strong>

                      <p>
                        The document passed the automated
                        evaluation criteria.
                      </p>
                    </div>
                  </div>
                )}

                {result.status === "FAIL" && (
                  <div className="fail-alert">
                    <div className="alert-icon">×</div>

                    <div>
                      <strong>
                        Extraction failure detected
                      </strong>

                      <p>
                        One or more evaluated fields do not
                        match the expected values.
                      </p>
                    </div>
                  </div>
                )}

                {/* RISK */}

                {(result.risk?.failed_fields?.length > 0 ||
                  result.risk?.low_confidence_fields
                    ?.length > 0) && (
                  <div className="risk-section">
                    <div className="section-title">
                      <span>RISK SIGNALS</span>
                    </div>

                    {result.risk.failed_fields?.length >
                      0 && (
                      <div className="risk-item failure">
                        <span className="risk-icon">
                          ×
                        </span>

                        <div>
                          <strong>
                            Failed fields
                          </strong>

                          <p>
                            {riskFieldNames(
                              result.risk.failed_fields
                            )
                              .map(formatFieldName)
                              .join(", ")}
                          </p>
                        </div>
                      </div>
                    )}

                    {result.risk
                      .low_confidence_fields
                      ?.length > 0 && (
                      <div className="risk-item warning">
                        <span className="risk-icon">
                          !
                        </span>

                        <div>
                          <strong>
                            Low-confidence fields
                          </strong>

                          <p>
                            {riskFieldNames(
                              result.risk.low_confidence_fields
                            )
                              .map(formatFieldName)
                              .join(", ")}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* FIELDS */}

                <div className="fields-section">
                  <div className="section-title">
                    <span>
                      EXTRACTED FIELDS
                    </span>

                    <small>
                      {
                        Object.keys(
                          result.fields || {}
                        ).length
                      }{" "}
                      fields
                    </small>
                  </div>

                  <div className="fields-list">
                    {Object.entries(
                      result.fields || {}
                    ).map(([fieldName, field]) => {
                      const confidence =
                        typeof field.confidence ===
                        "number"
                          ? field.confidence
                          : 0;

                      const level =
                        getConfidenceLevel(
                          confidence
                        );

                      const isFailed = hasRiskField(
                        result.risk?.failed_fields,
                        fieldName
                      );

                      const isLowConfidence = hasRiskField(
                        result.risk?.low_confidence_fields,
                        fieldName
                      );

                      return (
                        <div
                          className={`field-row ${level} ${
                            isFailed
                              ? "failed-field"
                              : ""
                          } ${
                            isLowConfidence
                              ? "review-field"
                              : ""
                          }`}
                          key={fieldName}
                        >
                          <div className="field-info">
                            <span className="field-name">
                              {formatFieldName(
                                fieldName
                              )}
                            </span>

                            <strong>
                              {field.value ||
                                "Not detected"}
                            </strong>

                            {isFailed && (
                              <span className="field-warning">
                                Extraction mismatch
                              </span>
                            )}

                            {!isFailed &&
                              isLowConfidence && (
                                <span className="field-warning">
                                  Low confidence
                                </span>
                              )}
                          </div>

                          <div className="confidence">
                            <div className="confidence-label">
                              <span>
                                {level === "low"
                                  ? "Low"
                                  : level === "medium"
                                  ? "Medium"
                                  : "High"}
                              </span>

                              <strong>
                                {confidence.toFixed(1)}%
                              </strong>
                            </div>

                            <div className="confidence-bar">
                              <div
                                style={{
                                  width: `${Math.min(
                                    confidence,
                                    100
                                  )}%`,
                                }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* OCR */}

                <div className="ocr-section">
                  <button
                    className="ocr-toggle"
                    onClick={() =>
                      setShowOcrText(
                        !showOcrText
                      )
                    }
                  >
                    <span>
                      <span className="terminal-icon">
                        &gt;_
                      </span>

                      OCR text
                    </span>

                    <span>
                      {showOcrText
                        ? "Hide ↑"
                        : "Show ↓"}
                    </span>
                  </button>

                  {showOcrText && (
                    <pre className="ocr-text">
                      {result.ocr_text ||
                        "No OCR text available."}
                    </pre>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <span>OCR Evaluator</span>
        <span>·</span>
        <span>
          Document Intelligence Evaluation Platform
        </span>
      </footer>
    </div>
  );
}

export default App;