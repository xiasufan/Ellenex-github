import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [url, setUrl] = useState('');
  const [keyword, setKeyword] = useState('');
  const [result, setResult] = useState({ summary: '', similarity: 0, keyword: '' });
  const [loading, setLoading] = useState(false);  // 添加loading状态

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);  // 请求开始时设置loading为true

    try {
      const response = await axios.post('http://localhost:5000/analyze', { url, keyword });
      console.log('API response:', response.data);  // 调试日志
      setResult({ ...response.data, keyword });  // 保存结果并包含关键词
    } catch (error) {
      console.error('Error fetching data:', error);
      setResult({ summary: 'Error', similarity: 0, keyword });
    } finally {
      setLoading(false);  // 请求完成后设置loading为false
    }
  };

  return (
    <div className="container">
      <h1>Website Analyzer</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter website URL"
        />
        <input
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="Enter a short description of your target market"
        />
        <button type="submit">Analyze</button>
      </form>
      <div className="results">
        {loading ? (  // 条件渲染加载指示器
          <p className="loading">Loading...</p>
        ) : (
          <>
            <h2>Results</h2>
            <p>Website Summary: {result.summary}</p>
            <p>Keyword: {result.keyword}</p>
            <p>Keyword Match Score: {result.similarity.toFixed(2)}</p>
          </>
        )}
      </div>
    </div>
  );
};

export default App;
