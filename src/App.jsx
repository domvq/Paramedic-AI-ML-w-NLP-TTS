
import { useState, useEffect } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  // ==========================================================
  // PATIENT
  // ==========================================================

  const [patient, setPatient] = useState({
    age: 50,
    heart_rate: 90,
    systolic_bp: 120,
    diastolic_bp: 80,
    respiratory_rate: 18,
    spo2: 98,
    temperature: 98.6,
  });

  const [assessment, setAssessment] = useState(null);
  const [assessmentLoading, setAssessmentLoading] =
    useState(false);
  const [assessmentError, setAssessmentError] =
    useState("");


  // ==========================================================
  // COPILOT
  // ==========================================================

  const [messages, setMessages] = useState([]);

  const [question, setQuestion] =
    useState("");

  const [copilotLoading, setCopilotLoading] =
    useState(false);

  const [copilotError, setCopilotError] =
    useState("");


  // ==========================================================
  // KNOWLEDGE
  // ==========================================================

  const [selectedFile, setSelectedFile] =
    useState(null);

  const [metadata, setMetadata] = useState({
    title: "",
    jurisdiction: "UNSPECIFIED",
    document_type:
      "educational_reference",
    effective_date: "",
    version: "",
    authority: "",
    status: "active",
    review_required: true,
  });

  const [uploadLoading, setUploadLoading] =
    useState(false);

  const [metadataLoading, setMetadataLoading] =
    useState(false);

  const [rebuildLoading, setRebuildLoading] =
    useState(false);

  const [knowledgeMessage, setKnowledgeMessage] =
    useState("");

  const [knowledgeError, setKnowledgeError] =
    useState("");

  const [registeredSources, setRegisteredSources] =
    useState([]);


  // ==========================================================
  // PATIENT FUNCTIONS
  // ==========================================================

  function updatePatient(field, value) {

    setPatient((previous) => ({
      ...previous,
      [field]: value,
    }));

  }


  async function runAssessment() {

    setAssessmentLoading(true);
    setAssessmentError("");
    setAssessment(null);

    try {

      const response =
        await fetch(
          `${API}/api/assessment`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify(patient),
          }
        );


      if (!response.ok) {

        const error =
          await response.json();

        throw new Error(
          error.detail ||
          `Server returned ${response.status}`
        );

      }


      const result =
        await response.json();

      setAssessment(result);

    } catch (error) {

      setAssessmentError(
        error.message ||
        "Unable to run assessment."
      );

    } finally {

      setAssessmentLoading(false);

    }

  }


  // ==========================================================
  // COPILOT FUNCTIONS
  // ==========================================================

  async function sendQuestion() {

    const text =
      question.trim();

    if (!text) {
      return;
    }


    const userMessage = {
      role: "user",
      content: text,
    };


    const updatedMessages = [
      ...messages,
      userMessage,
    ];


    setMessages(
      updatedMessages
    );

    setQuestion("");

    setCopilotLoading(true);
    setCopilotError("");


    try {

      const response =
        await fetch(
          `${API}/api/copilot`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              messages:
                updatedMessages,
            }),
          }
        );


      if (!response.ok) {

        const error =
          await response.json();

        throw new Error(
          error.detail ||
          "Copilot request failed."
        );

      }


      const result =
        await response.json();


      let answer =
        result.answer || "";


      if (
        result.references &&
        result.references.length
      ) {

        answer +=
          "\n\n📚 References used\n" +
          result.references
            .map(
              (reference) =>
                `• ${reference}`
            )
            .join("\n");

      }


      setMessages([
        ...updatedMessages,

        {
          role: "assistant",
          content: answer,
        },
      ]);

    } catch (error) {

      setCopilotError(
        error.message ||
        "Unable to connect to Copilot."
      );

    } finally {

      setCopilotLoading(false);

    }

  }


  function handleQuestionKeyDown(event) {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      sendQuestion();

    }

  }


  // ==========================================================
  // KNOWLEDGE FUNCTIONS
  // ==========================================================

  function updateMetadata(
    field,
    value
  ) {

    setMetadata(
      (previous) => ({
        ...previous,
        [field]: value,
      })
    );

  }


  function handleFileChange(
    event
  ) {

    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }


    setSelectedFile(file);

    setMetadata(
      (previous) => ({
        ...previous,

        title:
          previous.title ||
          file.name.replace(
            /\.[^/.]+$/,
            ""
          ),
      })
    );

    setKnowledgeMessage("");
    setKnowledgeError("");

  }


  async function uploadDocument() {

    if (!selectedFile) {

      setKnowledgeError(
        "Please choose a PDF or DOCX file."
      );

      return;
    }


    setUploadLoading(true);
    setKnowledgeMessage("");
    setKnowledgeError("");


    try {

      const formData =
        new FormData();

      formData.append(
        "file",
        selectedFile
      );


      const response =
        await fetch(
          `${API}/api/knowledge/upload`,
          {
            method: "POST",
            body: formData,
          }
        );


      if (!response.ok) {

        const error =
          await response.json();

        throw new Error(
          error.detail ||
          "Upload failed."
        );

      }


      const result =
        await response.json();


      setKnowledgeMessage(
        result.message ||
        "Document uploaded."
      );

    } catch (error) {

      setKnowledgeError(
        error.message ||
        "Document upload failed."
      );

    } finally {

      setUploadLoading(false);

    }

  }


  async function saveMetadata() {

    if (!selectedFile) {

      setKnowledgeError(
        "Please choose a document first."
      );

      return;
    }


    setMetadataLoading(true);
    setKnowledgeMessage("");
    setKnowledgeError("");


    try {

      const response =
        await fetch(
          `${API}/api/knowledge/metadata`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({

              filename:
                selectedFile.name,

              ...metadata,

              effective_date:
                metadata.effective_date ||
                null,

              version:
                metadata.version ||
                null,

            }),
          }
        );


      if (!response.ok) {

        const error =
          await response.json();

        throw new Error(
          error.detail ||
          "Metadata save failed."
        );

      }


      const result =
        await response.json();


      setKnowledgeMessage(
        result.message ||
        "Metadata saved."
      );


      loadRegisteredSources();

    } catch (error) {

      setKnowledgeError(
        error.message ||
        "Unable to save metadata."
      );

    } finally {

      setMetadataLoading(false);

    }

  }


  async function rebuildKnowledge() {

    setRebuildLoading(true);
    setKnowledgeMessage("");
    setKnowledgeError("");


    try {

      const response =
        await fetch(
          `${API}/api/knowledge/rebuild`,
          {
            method: "POST",
          }
        );


      if (!response.ok) {

        const error =
          await response.json();

        throw new Error(
          error.detail ||
          "Knowledge rebuild failed."
        );

      }


      const result =
        await response.json();


      setKnowledgeMessage(
        result.message ||
        "Knowledge index rebuilt successfully."
      );

    } catch (error) {

      setKnowledgeError(
        error.message ||
        "Unable to rebuild knowledge index."
      );

    } finally {

      setRebuildLoading(false);

    }

  }


  async function loadRegisteredSources() {

    try {

      const response =
        await fetch(
          `${API}/api/knowledge/sources`
        );


      if (!response.ok) {
        return;
      }


      const result =
        await response.json();


      setRegisteredSources(
        result.sources || []
      );

    } catch {
      // Ignore errors here
    }

  }


  useEffect(() => {

    loadRegisteredSources();

  }, []);


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div className="app">

<header className="header">

  <div className="brand">

    <div className="brand-icon">
      🚑
    </div>

    <div>
      <h1>Paramedic AI</h1>

      <p>
        EMS Education & Decision Support
      </p>
    </div>

  </div>


  <nav className="nav">

    <a href="#assessment">
      🩺 Assessment
    </a>

    <a href="#copilot">
      💬 Copilot
    </a>

    <a href="#knowledge">
      📚 Knowledge
    </a>

  </nav>


  <div className="demo-badge">
    DEMO MODE
  </div>

</header>



      <main className="container">


        {/* PATIENT ASSESSMENT */}

        <section className="card" id="assessment">

          <h2>
            🩺 Patient Assessment
          </h2>

          <p>
            Enter patient vital signs
            for the demonstration ML
            assessment.
          </p>


          <div className="form-grid">


            {[
              ["age", "Age"],
              [
                "heart_rate",
                "Heart Rate (bpm)",
              ],
              [
                "systolic_bp",
                "Systolic BP",
              ],
              [
                "diastolic_bp",
                "Diastolic BP",
              ],
              [
                "respiratory_rate",
                "Respiratory Rate (/min)",
              ],
              ["spo2", "SpO₂ (%)"],
              [
                "temperature",
                "Temperature (°F)",
              ],
            ].map(
              ([field, label]) => (

                <div
                  className="field"
                  key={field}
                >

                  <label>
                    {label}
                  </label>

                  <input

                    type="number"

                    step={
                      field ===
                      "temperature"
                        ? "0.1"
                        : "1"
                    }

                    value={
                      patient[field]
                    }

                    onChange={(event) =>
                      updatePatient(
                        field,
                        event.target.value
                      )
                    }

                  />

                </div>

              )
            )}

          </div>


          <button

            className="assessment-button"

            onClick={
              runAssessment
            }

            disabled={
              assessmentLoading
            }

          >

            {assessmentLoading
              ? "Running Assessment..."
              : "🧠 Run ML Assessment"}

          </button>


          {assessmentError && (

            <div className="error">

              ⚠️ {assessmentError}

            </div>

          )}

        </section>


        {/* RESULTS */}

        {assessment && (

          <section className="card">

            <h2>
              🧠 ML Risk Assessment
            </h2>


            <div className="result-grid">

              <div className="result-box">

                <span>
                  Estimated Risk Probability
                </span>

                <strong>

                  {(
                    assessment.probability *
                    100
                  ).toFixed(1)}
                  %

                </strong>

              </div>


              <div
                className={
                  assessment.category ===
                  "HIGHER RISK"
                    ? "risk higher"
                    : assessment.category ===
                      "INTERMEDIATE RISK"
                    ? "risk intermediate"
                    : "risk lower"
                }
              >

                {assessment.category}

              </div>

            </div>


            <div className="notice">

              This prediction is generated
              by a demonstration machine-learning
              model and is{" "}

              <strong>
                NOT a clinical diagnosis.
              </strong>

            </div>

          </section>

        )}


        {/* COPILOT */}

        <section className="card" id="copilot">

          <h2>
            💬 Paramedic Copilot
          </h2>

          <p>
            Ask questions about EMS
            education and your authorized
            reference materials.
          </p>


          <div className="chat-window">

            {messages.length === 0 && (

              <div className="chat-empty">

                🚑

                <strong>
                  Paramedic Copilot
                </strong>

                <span>
                  Ask an EMS education
                  question to get started.
                </span>

              </div>

            )}


            {messages.map(
              (message, index) => (

                <div
                  key={index}
                  className={`message ${message.role}`}
                >

                  <div className="message-label">

                    {message.role ===
                    "user"
                      ? "You"
                      : "Copilot"}

                  </div>

                  <div className="message-content">

                    {message.content}

                  </div>

                </div>

              )
            )}


            {copilotLoading && (

              <div className="message assistant">

                <div className="message-label">
                  Copilot
                </div>

                <div className="message-content">

                  Searching authorized
                  references and thinking...

                </div>

              </div>

            )}

          </div>


          {copilotError && (

            <div className="error">

              ⚠️ {copilotError}

            </div>

          )}


          <div className="chat-input-row">

            <textarea

              value={question}

              onChange={(event) =>
                setQuestion(
                  event.target.value
                )
              }

              onKeyDown={
                handleQuestionKeyDown
              }

              placeholder="Ask Paramedic AI a question..."

              rows="2"

            />


            <button

              className="send-button"

              onClick={
                sendQuestion
              }

              disabled={
                copilotLoading ||
                !question.trim()
              }

            >

              {copilotLoading
                ? "..."
                : "Send"}

            </button>

          </div>

        </section>


        {/* KNOWLEDGE MANAGER */}

        <section className="card" id="knowledge">

          <h2>
            📚 Knowledge Manager
          </h2>

          <p>
            Upload and manage authorized
            EMS reference documents.
          </p>


          <div className="upload-box">

            <label>
              Reference Document
            </label>

            <input
              type="file"
              accept=".pdf,.docx"
              onChange={
                handleFileChange
              }
            />


            {selectedFile && (

              <p>
                📄 {selectedFile.name}
              </p>

            )}


            <button

              className="secondary-button"

              onClick={
                uploadDocument
              }

              disabled={
                !selectedFile ||
                uploadLoading
              }

            >

              {uploadLoading
                ? "Uploading..."
                : "📤 Upload Document"}

            </button>

          </div>


          {selectedFile && (

            <div className="metadata">

              <h3>
                Source Metadata
              </h3>


              <div className="form-grid">


                <div className="field">

                  <label>
                    Title
                  </label>

                  <input
                    value={
                      metadata.title
                    }
                    onChange={(e) =>
                      updateMetadata(
                        "title",
                        e.target.value
                      )
                    }
                  />

                </div>


                <div className="field">

                  <label>
                    Jurisdiction
                  </label>

                  <input
                    value={
                      metadata.jurisdiction
                    }
                    onChange={(e) =>
                      updateMetadata(
                        "jurisdiction",
                        e.target.value
                      )
                    }
                  />

                </div>


                <div className="field">

                  <label>
                    Document Type
                  </label>

                  <select
                    value={
                      metadata.document_type
                    }
                    onChange={(e) =>
                      updateMetadata(
                        "document_type",
                        e.target.value
                      )
                    }
                  >

                    <option value="educational_reference">
                      Educational Reference
                    </option>

                    <option value="agency_protocol">
                      Agency Protocol
                    </option>

                    <option value="medical_director_order">
                      Medical Director Order
                    </option>

                    <option value="manufacturer_reference">
                      Manufacturer Reference
                    </option>

                    <option value="other">
                      Other
                    </option>

                  </select>

                </div>


                <div className="field">

                  <label>
                    Effective Date
                  </label>

                  <input
                    type="date"
                    value={
                      metadata.effective_date
                    }
                    onChange={(e) =>
                      updateMetadata(
                        "effective_date",
                        e.target.value
                      )
                    }
                  />

                </div>


                <div className="field">

                  <label>
                    Version
                  </label>

                  <input
                    value={
                      metadata.version
                    }
                    onChange={(e) =>
                      updateMetadata(
                        "version",
                        e.target.value
                      )
                    }
                  />

                </div>


                <div className="field">

                  <label>
                    Authority
                  </label>

                  <input
                    value={
                      metadata.authority
                    }
                    onChange={(e) =>
                      updateMetadata(
                        "authority",
                        e.target.value
                      )
                    }
                  />

                </div>


                <div className="field">

                  <label>
                    Status
                  </label>

                  <select
                    value={
                      metadata.status
                    }
                    onChange={(e) =>
                      updateMetadata(
                        "status",
                        e.target.value
                      )
                    }
                  >

                    <option value="active">
                      Active
                    </option>

                    <option value="draft">
                      Draft
                    </option>

                    <option value="inactive">
                      Inactive
                    </option>

                    <option value="retired">
                      Retired
                    </option>

                    <option value="superseded">
                      Superseded
                    </option>

                  </select>

                </div>


                <div className="field">

                  <label>

                    <input
                      type="checkbox"
                      checked={
                        metadata.review_required
                      }
                      onChange={(e) =>
                        updateMetadata(
                          "review_required",
                          e.target.checked
                        )
                      }
                    />

                    {" "}Requires review

                  </label>

                </div>

              </div>


              <button

                className="assessment-button"

                onClick={
                  saveMetadata
                }

                disabled={
                  metadataLoading
                }

              >

                {metadataLoading
                  ? "Saving..."
                  : "💾 Save Metadata"}

              </button>

            </div>

          )}


          <div className="rebuild-box">

            <h3>
              🔄 Knowledge Index
            </h3>

            <p>
              Rebuild the knowledge index
              after adding or changing
              reference documents.
            </p>

            <button

              className="rebuild-button"

              onClick={
                rebuildKnowledge
              }

              disabled={
                rebuildLoading
              }

            >

              {rebuildLoading
                ? "Rebuilding..."
                : "🔄 Ingest & Rebuild Knowledge Index"}

            </button>

          </div>


          {knowledgeMessage && (

            <div className="success-message">

              ✓ {knowledgeMessage}

            </div>

          )}


          {knowledgeError && (

            <div className="error">

              ⚠️ {knowledgeError}

            </div>

          )}


          <div className="sources">

            <h3>
              📖 Registered Sources
            </h3>


            {registeredSources.length === 0 ? (

              <p>
                No registered sources found.
              </p>

            ) : (

              registeredSources.map(
                (source, index) => (

                  <div
                    className="source-card"
                    key={index}
                  >

                    <h4>
                      📄{" "}
                      {source.title ||
                        source.filename}
                    </h4>

                    <p>
                      File:{" "}
                      {source.filename}
                    </p>

                    <p>
                      Jurisdiction:{" "}
                      {source.jurisdiction ||
                        "UNSPECIFIED"}
                    </p>

                    <p>
                      Type:{" "}
                      {source.document_type ||
                        "UNKNOWN"}
                    </p>

                    <p>
                      Status:{" "}
                      {source.status ||
                        "UNKNOWN"}
                    </p>

                    {source.review_required
                      ? (
                        <div className="review-warning">
                          ⚠️ Review required
                        </div>
                      )
                      : (
                        <div className="review-complete">
                          ✓ Review complete
                        </div>
                      )}

                  </div>

                )
              )

            )}

          </div>

        </section>


        {/* SAFETY */}

        <section className="safety">

          <strong>
            DEMO ONLY — NOT FOR
            CLINICAL DECISION MAKING.
          </strong>

          <p>
            Always follow current local
            EMS protocols, medical direction,
            scope of practice, manufacturer
            instructions, and applicable
            regulations.
          </p>

        </section>

      </main>

    </div>

  );
}

export default App;
