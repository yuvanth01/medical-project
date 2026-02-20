import React, { useState } from "react";

function Upload() {
  const [file, setFile] = useState(null);
  const [responseData, setResponseData] = useState(null);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload-medical-bill/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("Backend Response:", data);

      setResponseData(data); // store full response
    } catch (error) {
      console.error("Upload Error:", error);
      alert("Upload failed");
    }
  };

  return (
    <div style={{ padding: "40px" }}>
      <h2>Medical Bill OCR</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button onClick={handleUpload}>
        Upload
      </button>

      {responseData && (
        <div style={{ marginTop: "20px", border: "1px solid black", padding: "10px" }}>
          <h3>Backend Response:</h3>
          <pre>{JSON.stringify(responseData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default Upload;