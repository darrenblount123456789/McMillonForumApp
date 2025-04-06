import React, { useState } from 'react';

const UploadTextBox = ({ onUploadText }) => {
  const [text, setText] = useState('');

  const handleUpload = () => {
    if (text.trim() !== '') {
      onUploadText(text);
      setText(''); // Clear input field after upload
    }
  };

  return (
    <div className="uploadTextBox">
      <input 
        type="text" 
        placeholder="Enter text here..." 
        value={text} 
        onChange={(e) => setText(e.target.value)} 
      />
      <button onClick={handleUpload}>Click to Upload</button>
    </div>
  );
};

export default UploadTextBox;
