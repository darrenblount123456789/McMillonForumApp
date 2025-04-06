import React from 'react';

const UploadFileBox = ({ onUploadFile }) => {
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();
      console.log(" File uploaded successfully:", data);

      // Update the document list after successful upload
      onUploadFile(data);
    } catch (error) {
      console.error(" Error uploading file:", error);
    }
  };

  return (
    <div className="uploadFileBox">
      <input type="file" accept=".pdf,.docx" onChange={handleFileChange} />
      <button onClick={() => document.getElementById('fileInput').click()}>Upload Document</button>
      <input id="fileInput" type="file" accept=".pdf,.docx" onChange={handleFileChange} style={{ display: 'none' }} />
    </div>
  );
};

export default UploadFileBox;
