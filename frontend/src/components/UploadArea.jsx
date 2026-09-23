import { useRef, useState } from "react";
import { uploadFile } from "../api/ocr.api";

export default function UploadArea({ onNewJob }) {
  const inputRef = useRef(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const handleFile = async (file) => {
    if (!file || busy) return;

    setBusy(true);
    setError("");

    try {
      const uploadRes = await uploadFile(file);
      if (!uploadRes?.id) {
        throw new Error("Invalid upload response");
      }

      onNewJob({
        id: uploadRes.id,
        filename: file.name,
        status: uploadRes.status,
      });
    } catch (err) {
      console.error(err);
      setError("Upload failed. Please try again.");
    } finally {
      setBusy(false);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  };

  return (
    <div
      className={`upload-area ${busy ? "disabled" : ""}`}
      role="button"
      tabIndex={0}
      aria-disabled={busy}
      onClick={() => !busy && inputRef.current?.click()}
      onKeyDown={(e) =>
        !busy && (e.key === "Enter" || e.key === " ") && inputRef.current?.click()
      }
    >
      <input
        ref={inputRef}
        hidden
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.txt"
        onChange={(e) => handleFile(e.target.files[0])}
      />

      {!busy ? (
        <span>Click here to upload a file</span>
      ) : (
        <p>Uploading…</p>
      )}

      {error && <p className="error">{error}</p>}

      <p className="hint">
        Processing happens in the background — search for your document once it's ready.
      </p>
    </div>
  );
}