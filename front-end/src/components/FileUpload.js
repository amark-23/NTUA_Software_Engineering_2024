import React from 'react';

function FileUpload({ onFileChange }) {
  return (
    <div>
      <label>Upload CSV:</label>
      <input type="file" accept=".csv" onChange={onFileChange} />
    </div>
  );
}

export default FileUpload;

