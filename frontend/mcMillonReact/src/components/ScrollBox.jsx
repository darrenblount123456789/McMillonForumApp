import React from 'react';
import DocumentThumbnail from './DocumentThumbnail';

const ScrollBox = ({ entries, documents, onClickDocument }) => {
  return (
    <div className="scrollBox">
      {entries.length === 0 && documents.length === 0 ? (
        <p>No uploads yet.</p>
      ) : (
        <>
          {entries.map((entry, index) => (
            <p key={index} className="text-entry">{entry}</p>
          ))}
          {documents.map((file, index) => (
            <DocumentThumbnail key={index} file={file} onClick={() => onClickDocument(file.file_url)} />
          ))}
        </>
      )}
    </div>
  );
};

export default ScrollBox;
