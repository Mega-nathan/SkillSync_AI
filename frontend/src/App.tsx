import { useState, useRef, DragEvent } from "react";
import "./App.css";

function App() {
  const [fileName, setFileName] = useState<string | null>(null);
  const [jobText, setJobText] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  function onDrop(e: DragEvent) {
    e.preventDefault();
    const f = e.dataTransfer.files && e.dataTransfer.files[0];
    if (f) setFileName(f.name);
  }

  function onDragOver(e: DragEvent) {
    e.preventDefault();
  }

  function clearFile() {
    setFileName(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  async function uploadResume(file: File) {
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://127.0.0.1:8000/resume/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      console.log("Parsed Resume:", data);

      // Store parsed data if required
      // setParsedResume(data);
    } catch (error) {
      console.error("Error uploading resume:", error);
    }
  }

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files && e.target.files[0];
    if (f) {
      setFileName(f.name);
      uploadResume(f);
    }
  }

  return (
    <div className="page-root">
      <div className="container">
        <div className="panel left-panel">
          <div className="step">STEP. 01</div>
          <h2 className="panel-title">Resume Source</h2>
          <p className="panel-sub">
            Upload your current resume in PDF or DOCX format for AI structural
            analysis.
          </p>

          <div
            className="upload-area"
            onDrop={onDrop}
            onDragOver={onDragOver}
            onClick={() => fileInputRef.current?.click()}
          >
            {!fileName ? (
              <>
                <div className="upload-icon" />
                <div className="upload-text">Upload your Resume</div>
                <div className="upload-hint">
                  Drag and drop your document here or click to browse files from
                  your computer.
                </div>
                <div className="upload-buttons">
                  <button className="btn btn-outline">PDF</button>
                  <button className="btn btn-outline">DOCX</button>
                </div>
              </>
            ) : (
              <div className="file-info">
                <div className="file-name">{fileName}</div>
                <button
                  className="btn btn-clear"
                  onClick={(e) => {
                    e.stopPropagation();
                    clearFile();
                  }}
                >
                  Remove
                </button>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,.docx"
              onChange={onFileChange}
              style={{ display: "none" }}
            />
          </div>
        </div>

        <div className="panel right-panel">
          <div className="step">STEP. 02</div>
          <h2 className="panel-title">Target Job Information</h2>
          <p className="panel-sub">
            Paste the job requirements to evaluate your alignment score and
            missing skills.
          </p>

          <div className="job-card">
            <div className="job-card-header">
              JOB DESCRIPTION <button className="paste-btn">Paste Text</button>
            </div>
            <textarea
              className="job-textarea"
              placeholder="Enter the job description to compare against your resume..."
              value={jobText}
              onChange={(e) => setJobText(e.target.value)}
            />

            <div className="analyze-row">
              <div className="ready">READY FOR ANALYSIS</div>
              <button className="btn btn-primary">Analyze Match ⚡</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
