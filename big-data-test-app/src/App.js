import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [textBoxes, setTextBoxes] = useState(['']);
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const addTextBox = () => {
    setTextBoxes([...textBoxes, '']);
  };

  const handleChange = (index, value) => {
    const newTextBoxes = [...textBoxes];
    newTextBoxes[index] = value;
    setTextBoxes(newTextBoxes);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/analyze', { texts: textBoxes });
      setFeedback(response.data);
    } catch (err) {
      console.error('Error analyzing text:', err);
      setError('Failed to analyze the text.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>React and Flask Integration</h1>
      {textBoxes.map((text, index) => (
        <textarea
          key={index}
          value={text}
          onChange={(e) => handleChange(index, e.target.value)}
          placeholder={`Enter text ${index + 1}`}
        />
      ))}
      <button onClick={addTextBox}>Add Text Box</button>
      <button onClick={handleAnalyze}>Analyze</button>
      {loading && <div>Loading...</div>}
      {error && <div>{error}</div>}
      {!loading && !error && feedback && (
        <div>
          <h3>Feedback</h3>
          <pre>{feedback}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
