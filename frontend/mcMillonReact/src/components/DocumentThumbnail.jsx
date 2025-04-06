import React, { useState, useEffect } from "react";
import mammoth from "mammoth";
import html2canvas from "html2canvas";

const DocumentThumbnail = ({ file, onClick }) => {
  const [thumbnail, setThumbnail] = useState(null);
  const [documentName, setDocumentName] = useState("Loading...");

  useEffect(() => {
    if (!file?.file_name || !file?.file_url) return; // Ensure file data exists

    setDocumentName(file.file_name); // Display correct filename

    // if (file.file_name.endsWith(".docx")) {
    //   fetch(file.file_url) // Fetch document from S3 URL
    //     .then((res) => res.arrayBuffer())
    //     .then(async (arrayBuffer) => {
    //       try {
    //         // Extract text
    //         const textResult = await mammoth.extractRawText({ arrayBuffer });

    //         // Create a div to hold the content
    //         const container = document.createElement("div");
    //         container.style.width = "800px";
    //         container.style.height = "400px";
    //         container.style.padding = "20px";
    //         container.style.backgroundColor = "#fff";
    //         container.style.border = "1px solid #ccc";
    //         container.style.fontFamily = "'Times New Roman', serif";
    //         container.innerText = textResult.value;

    //         document.body.appendChild(container);

    //         // Capture the content as an image
    //         setTimeout(() => {
    //           html2canvas(container, { scale: 2 }).then((canvas) => {
    //             setThumbnail(canvas.toDataURL("image/png"));
    //             document.body.removeChild(container);
    //           });
    //         }, 500);
    //       } catch (error) {
    //         console.error("Failed to process DOCX:", error);
    //       }
    //     })
    //     .catch((err) => console.error("Error fetching document:", err));
    // }
  }, [file]);

  return (
  <div className="documentThumbnail" onClick={() => onClick(file.file_url || "")}>
    {/*thumbnail ? (
        <img src={thumbnail} alt="DOCX Preview" width="150" />
      ) : (
        <p>Generating preview...</p>
      )*/}
      <p>{documentName}</p>
    </div>
  );
};

export default DocumentThumbnail;
