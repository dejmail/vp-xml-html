import React, { useState } from 'react';
import FileUpload from './FileUpload';

const App = () => {
  const [message, setMessage] = useState("");
  const [classes, setClasses] = useState([]);
  const [selectedClasses, setSelectedClasses] = useState([]);
  const [generatedHtml, setGeneratedHtml] = useState(""); // Store the generated HTML here
  const [disabledClasses, setDisabledClasses] = useState([]);




  const handleFilesUploaded = (responseData) => {
    if (responseData) {
      if (responseData.html) {
        setGeneratedHtml(responseData.html);  // Set the generated HTML
      }
      if (responseData.classes) {
        setClasses(responseData.classes);  // Set the list of classes
        setSelectedClasses(responseData.classes);  // Pre-select all classes by default
      }
    } else {
      setMessage("No HTML or class content found in the response.");
    }
  };
  
  const handleClassToggle = (className) => {
    setSelectedClasses((prevSelected) => {
      let updatedSelected;
      if (prevSelected.includes(className)) {
        // If the class is already selected, remove it and disable it
        updatedSelected = prevSelected.filter((name) => name !== className);
        setDisabledClasses((prevDisabled) => [...prevDisabled, className]);
      } else {
        // If the class is not selected, add it
        updatedSelected = [...prevSelected, className];
      }
  
      // Update the generated HTML preview
      const filteredHtml = generateHtmlContent();
      setGeneratedHtml(filteredHtml);
  
      return updatedSelected;
    });
  };


  const generateHtmlContent = () => {
    if (!generatedHtml) {
      return "";
    }
  
    // Parse the full HTML document from generatedHtml
    const parser = new DOMParser();
    const doc = parser.parseFromString(generatedHtml, "text/html");
  
    // Find all <h2> elements (or appropriate elements representing class headers)
    const h2Elements = doc.querySelectorAll("h2");
  
    // Iterate over <h2> elements and remove those that are not in selectedClasses
    h2Elements.forEach((h2) => {
      const className = h2.textContent.trim();
  
      // If the class is not selected, remove the <h2> and its subsequent siblings
      if (!selectedClasses.includes(className)) {
        let currentElement = h2;
  
        while (currentElement) {
          const nextElement = currentElement.nextElementSibling;
  
          // Remove the current element from the DOM
          currentElement.remove();
  
          // Stop when reaching another <h2> or no more siblings
          if (nextElement && nextElement.tagName === "H2") {
            break;
          }
  
          currentElement = nextElement;
        }
      }
    });
  
    // Return the entire updated document as a string, including the <head> and <body>
    return doc.documentElement.outerHTML;
  };
  
    

  const handleDownload = () => {
    if (!generatedHtml) {
      setMessage("No HTML available to download. Please generate the HTML first.");
      return;
    }
  
    // Create a blob from the filtered HTML content and trigger the download
    const blob = new Blob([generatedHtml], { type: 'text/html' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'filtered_classes.html';
    link.click();
  };

  
  return (
    <div className="App">

      <h1 className="text-2xl font-bold text-center mb-6">Visual Paradigm XML to HTML Converter</h1>

      {/* GitHub Icon */}
      <div className="center pb-3">
        <a href="https://github.com/dejmail/vp-xml-html.git" target="_blank" rel="noopener noreferrer">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-8 w-8 text-gray-800 hover:text-gray-600"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M12 2C6.477 2 2 6.486 2 12.018a10.013 10.013 0 006.839 9.524c.5.093.682-.217.682-.482 0-.237-.009-.866-.014-1.7-2.782.607-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.465-1.11-1.465-.908-.621.069-.608.069-.608 1.004.071 1.533 1.034 1.533 1.034.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.089.637-1.34-2.22-.254-4.555-1.114-4.555-4.951 0-1.093.39-1.987 1.029-2.687-.103-.254-.446-1.276.098-2.66 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 7.044c.851.004 1.705.115 2.504.337 1.91-1.294 2.749-1.025 2.749-1.025.545 1.384.201 2.406.099 2.66.64.7 1.028 1.594 1.028 2.687 0 3.847-2.337 4.694-4.564 4.943.36.31.68.92.68 1.855 0 1.34-.013 2.419-.013 2.747 0 .268.18.579.688.481A10.015 10.015 0 0022 12.018C22 6.486 17.523 2 12 2z"
              clipRule="evenodd"
            />
          </svg>
        </a>
      </div>

      {/* File Upload Section */}
      <FileUpload onFilesUploaded={handleFilesUploaded} />
  
      <div className="my-4 text-center text-red-500">{message}</div>
  
      {/* Display Classes for Selection */}
{classes && classes.length > 0 && (
  <div className="class-selection w-full max-w-lg mx-auto p-4 border rounded shadow">
    <h2 className="text-xl font-bold mb-4">Select Classes to Include in HTML</h2>
    <ul>
      {classes.map((className) => (
        <li key={className} className="my-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={selectedClasses.includes(className)}
              disabled={disabledClasses.includes(className)}
              onChange={() => handleClassToggle(className)}
              className="mr-2"
            />
            {className}
          </label>
        </li>
      ))}
    </ul>
    <button
      onClick={() => setGeneratedHtml(generateHtmlContent())}
      className="mt-4 w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition duration-300"
    >
      Generate HTML Preview
    </button>
  </div>
)}
  
      {/* HTML Preview and Download Button */}
      {generatedHtml && (
  <div className="row my-4">
    <div className="w-full max-w-lg mx-auto p-4 border rounded shadow">
      <h2 className="text-xl font-bold mb-4">HTML Preview</h2>
      <iframe
        title="HTML Preview"
        className="w-full border p-2"
        style={{ height: "600px" }}
        srcDoc={generatedHtml} // Use `srcDoc` to embed the entire HTML document
      />
      <button
        onClick={handleDownload}
        className="mt-4 w-full bg-green-500 text-white py-2 px-4 rounded-lg hover:bg-green-600 transition duration-300"
      >
        Download HTML File
      </button>
    </div>
  </div>
)}
    </div>
  );
};

export default App;
