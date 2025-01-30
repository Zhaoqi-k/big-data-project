import React, { useState } from "react";
import axios from "axios";

function App() {
  const [reportCard, setReportCard] = useState(""); // Single input
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [emojiFeedback, setEmojiFeedback] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setFeedback(null);

    try {
      const response = await axios.post("http://127.0.0.1:5000/analyze", {
        text: reportCard, // Send single text input
      });

      console.log("Response received:", response.data);
      setFeedback(response.data);
    } catch (err) {
      console.error("Error analyzing text:", err);
      setError("Failed to analyze the text.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      height: "100vh",
      backgroundColor: "#fff",
      color: "#000",
      fontFamily: "Arial, sans-serif",
    }}>
      <h1 style={{ color: "#e60000", marginBottom: "20px" }}>AI Report Card Analysis</h1>
      <textarea
        value={reportCard}
        onChange={(e) => setReportCard(e.target.value)}
        placeholder="Paste the student's report card here..."
        rows={6}
        cols={50}
        style={{
          padding: "10px",
          borderRadius: "5px",
          border: "2px solid #e60000",
          backgroundColor: "#f8f8f8",
          color: "#000",
          fontSize: "16px",
          width: "80%",
          marginBottom: "15px",
        }}
      />
      <button
        onClick={handleAnalyze}
        style={{
          backgroundColor: "#e60000",
          color: "#fff",
          padding: "10px 20px",
          fontSize: "16px",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
          marginBottom: "20px",
        }}
      >
        Analyze
      </button>
      {loading && <div>Loading...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
      {!loading && !error && feedback && (
        <div style={{
          backgroundColor: "#f0f0f0",
          padding: "20px",
          borderRadius: "8px",
          width: "80%",
          textAlign: "left",
          position: "relative"
        }}>
          <h3 style={{ color: "#e60000" }}>AI Feedback</h3>
          <p><strong>Strengths:</strong></p>
          <ul>
            {feedback.strengths.map((strength, index) => (
              <li key={index}>{strength}</li>
            ))}
          </ul>
          <p><strong>Areas to Improve:</strong></p>
          <ul>
            {feedback.areas_to_improve.map((area, index) => (
              <li key={index}>{area}</li>
            ))}
          </ul>
          <div style={{
            display: "flex",
            justifyContent: "center",
            marginTop: "10px"
          }}>
            {['🔥', '❤️', '😡', '😊', '😭'].map((emoji) => (
              <span
                key={emoji}
                onClick={() => setEmojiFeedback(emoji)}
                style={{
                  fontSize: "24px",
                  cursor: "pointer",
                  margin: "5px",
                  padding: "5px"
                }}
              >
                {emoji}
              </span>
            ))}
          </div>
          {emojiFeedback && <p style={{ textAlign: "center", marginTop: "5px" }}>You reacted with: {emojiFeedback}</p>}
        </div>
      )}
    </div>
  );
}

export default App;
