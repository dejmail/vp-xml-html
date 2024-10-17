import React, { useState } from 'react';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [header, setHeader] = useState("");
  const [message, setMessage] = useState("");
  const [generatedHtml, setGeneratedHtml] = useState(null);


  // Function to handle file input change
  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  // Function to handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!file) {
      setMessage("Välja en fil först");
      return;
    }

    // Create a FormData object to send file data
    const formData = new FormData();
    formData.append('header', header)
    formData.append('file', file);

    try {
      // Send the file to the Flask backend
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setMessage(`Fil uppladdad: ${result.message}`);
      } else {
        setMessage("Fel med uppladdning. Försök igen.");
      }
    } catch (error) {
      console.error("Fel med uppladdning:", error);
      setMessage("Fel med uppladdning. Försök igen.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="file" className="block text-gray-700 text-center font-medium mb-4">Välja ZIP fil exporterat från Visual Paradigm</label>
            <input
              type="file"
              id="file"
              onChange={handleFileChange}
              accept=".zip"
              className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none"
            />
          </div>
          <button type="submit" className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition duration-300">
            Ladda Upp
          </button>
        </form>
        {message && (
          <p className="mt-4 text-center text-sm text-gray-700">{message}</p>
        )}
      </div>
    </div>
  );
}

export default FileUpload;
