import { useState, useEffect } from 'react';
import './App.css';
import UploadTextBox from './components/UploadTextBox.jsx';
import UploadFileBox from './components/UploadFileBox.jsx';
import ScrollBox from './components/ScrollBox.jsx';

function App() {
  const [entries, setEntries] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [aiResponse, setAiResponse] = useState("");

  const fetchDocuments = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/files/");
      if (!response.ok) {
        throw new Error("Failed to fetch documents");
      }
      const data = await response.json();
  
      console.log(" Documents received:", data);
      setDocuments(data);
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUploadText = (text) => {
    setEntries((prev) => [...prev, text]);
  };

  const handleUploadFile = (uploadedFile) => {
    setDocuments((prev) => [...prev, uploadedFile]); 
  };

  const openFullDocument = (fileUrl) => {
    if (!fileUrl || typeof fileUrl !== "string") {
      console.error("File URL is missing or invalid:", fileUrl);
      return;
    }
    console.log("Opening file:", fileUrl);
    window.open(fileUrl, "_blank");
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      const response = await fetch(`http://127.0.0.1:8000/search/?query=${encodeURIComponent(searchQuery)}`);
      if (!response.ok) {
        throw new Error("Failed to fetch search results");
      }
      const data = await response.json();

      console.log("🔍 Search results:", data);
      setAiResponse(data.response);
      setSearchResults(data.results);
    } catch (error) {
      console.error("Error searching documents:", error);
    }
  };

  return (
    <>
      <h1>McMillon Forum</h1>

      {/* Search Bar */}
      <div className="searchBar">
        <input 
          type="text" 
          value={searchQuery} 
          onChange={(e) => setSearchQuery(e.target.value)} 
          placeholder="Search for documents..."
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      {/* Display AI Response */}
      {aiResponse && (
        <div className="aiResponse">
          <h2>AI Response:</h2>
          <p>{aiResponse}</p>
        </div>
      )}

      {/* Display Search Results */}
      {searchResults.length > 0 && (
        <ScrollBox entries={entries} documents={searchResults} onClickDocument={openFullDocument} />
      )}

      {/* Upload Section */}
      <UploadTextBox onUploadText={handleUploadText} />
      <UploadFileBox onUploadFile={handleUploadFile} />

      {/* Default Document List (if no search) */}
      {searchResults.length === 0 && (
        <ScrollBox entries={entries} documents={documents} onClickDocument={openFullDocument} />
      )}
    </>
  );
}

export default App;
