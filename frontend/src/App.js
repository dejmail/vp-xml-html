

import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';

function App() {
  const [file, setFile] = useState(null);
  const [header, setHeader] = useState("");
  const [message, setMessage] = useState("");
  const [generatedHtml, setGeneratedHtml] = useState(null);

  // Handle file input change
  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  // Handle header input change
  const handleHeaderChange = (event) => {
    setHeader(event.target.value);
  };

  // Handle file upload form submission
  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!file) {
      setMessage("Please choose a file first.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('header', header);

    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setGeneratedHtml(result.html);
        setMessage("Fil uppladdad.");
      } else {
        const errorResult = await response.json();
        setMessage(`Fel med uppladdning. Vänligen försök igen. - ${errorResult.message}`);
      }
    } catch (error) {
      console.error("Fel med uppladdning:", error);
      setMessage("Fel med uppladdning. Vänligen försök igen.");
    }
  };

  // Function to trigger download of the generated HTML
  const handleDownload = () => {
    const element = document.createElement('a');
    const fileBlob = new Blob([generatedHtml], { type: 'text/html' });
    element.href = URL.createObjectURL(fileBlob);
    element.download = "generated.html";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (

    <div className="flex items-center justify-center min-h-screen bg-gray-100">
    <div className="w-full max-w-lg mx-auto p-4 border rounded shadow bg-white">
      
    <div className="container">
      <div className="row my-4">
        <h1 className="text-1xl font-bold mb-6 text-center text-gray-800">
          Visual Paradigm XML-HTML omvandlare
        </h1>
        {/* GitHub Icon Link */}
        <div className="text-center my-4">
          <a href="https://github.com/dejmail/vp-xml-html" target="_blank" rel="noopener noreferrer">
            <FontAwesomeIcon icon={faGithub} size="2x" className="text-gray-800 hover:text-black transition duration-300" />
          </a>
        </div>
      </div>

      {/* File Upload Form */}
      <div className="row my-4">
        <form onSubmit={handleSubmit} className="w-full max-w-lg mx-auto p-4 border rounded shadow">
          <div className="mb-4">
            <label htmlFor="file" className="block text-gray-700 font-medium mb-2">Välja ZIP fil</label>
            <input
              type="file"
              id="file"
              onChange={handleFileChange}
              accept=".zip"
              className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none"
            />
          </div>
          <div className="mb-4">
            <label htmlFor="header" className="block text-gray-700 font-medium mb-2">Rubrik till genererat HTML</label>
            <input
              type="text"
              id="header"
              value={header}
              onChange={handleHeaderChange}
              placeholder="Skriva ett förslag till huvud rubrik"
              className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg p-2 focus:outline-none"
            />
          </div>
          <button type="submit" className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition duration-300">
            Ladd upp fil
          </button>
        </form>
        {message && <p className="mt-4 text-center text-sm text-gray-700">{message}</p>}
      </div>

      {/* Display Generated HTML and Download Option */}
      {generatedHtml && (
        <div className="row my-4">
          <div className="w-full max-w-lg mx-auto p-4 border rounded shadow">
            <h2 className="text-xl font-bold mb-4">HTML Utkast</h2>
            <div
              className="generated-html-preview border p-2"
              dangerouslySetInnerHTML={{ __html: generatedHtml }}
            />
            <button
              onClick={handleDownload}
              className="mt-4 w-full bg-green-500 text-white py-2 px-4 rounded-lg hover:bg-green-600 transition duration-300">
              Ladda ner HTML fil
            </button>
          </div>
        </div>
      )}
    </div>
    </div>
    </div>
  );
}

export default App;
