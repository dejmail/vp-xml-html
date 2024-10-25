import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

const FileUpload = ({ onFilesUploaded }) => {
  const [files, setFiles] = useState([]);
  const [message, setMessage] = useState("");

  const onDrop = useCallback((acceptedFiles) => {
    // Store the files dropped
    setFiles(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: ".zip,.svg,.xml", // Accept SVG and XML files
    multiple: true, // Allow multiple file uploads
  });

  const handleUpload = async () => {
    // Check if we have both required files: SVG and XML
    const svgFile = files.find(file => file.name.endsWith('.svg'));
    const xmlFile = files.find(file => file.name.endsWith('.xml'));
    if (!svgFile || !xmlFile) {
      setMessage("Please upload both SVG and project.xml files.");
      return;
    }

    const formData = new FormData();
    formData.append('svg', svgFile);
    formData.append('xml', xmlFile);

    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        onFilesUploaded(data);
        setMessage("Files uploaded and classes extracted successfully.");
      } else {
        const errorResult = await response.json();
        setMessage(`Upload failed. Please try again. - ${errorResult.message}`);
      }
    } catch (error) {
      console.error("Upload failed:", error);
      setMessage("Upload failed. Please try again.");
    }
  };

  return (
    <div className="file-upload">
      <div
        {...getRootProps({
          className: 'dropzone w-full max-w-lg mx-auto p-6 border-2 border-dashed rounded cursor-pointer text-center',
        })}
      >
        <input {...getInputProps()} />
        <p>Drag & drop the SVG and XML files here, or click to select files</p>
      </div>
      
      {files.length > 0 && (

<div class="mt-4 p-4 border border-gray-200 rounded-lg shadow-lg bg-gray-50 w-1/6 mx-auto">
  <strong class="block text-lg font-semibold text-gray-700 mb-2">Selected Files:</strong>
  <ul class="list-disc list-inside text-gray-600">
            {files.map(file => (
              <li key={file.name}>{file.name}</li>
            ))}
          </ul>
        </div>
      )}

      <button
        onClick={handleUpload}
        className="w-1/6 mx-auto mt-4 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition duration-300 block"
        

      >
        Upload and Extract Classes
      </button>
      
      <div className="my-4 text-center text-red-500">{message}</div>
    </div>
  );
};

export default FileUpload;
