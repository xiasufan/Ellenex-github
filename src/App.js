// src/App.js
import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import './App.css';

function App() {
  const [data, setData] = useState([]);

  const handleFileUpload = (uploadedData) => {
    setData(uploadedData);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>CSV Upload and Display</h1>
        <FileUpload onFileUpload={handleFileUpload} />
        {data.length > 0 && (
          <table>
            <thead>
              <tr>
                {Object.keys(data[0]).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr key={index}>
                  {Object.values(row).map((value, i) => (
                    <td key={i}>{value}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </header>
    </div>
  );
}

export default App;
