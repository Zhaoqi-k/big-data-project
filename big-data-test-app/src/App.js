import React, { useState } from "react";
import axios from "axios";
import "./App.css"

function App() {
  const [reportCard, setReportCard] = useState(null); // Single input
  const [feedback, setFeedback] = useState(null);
  const [studentID, setStudentID] = useState("");
  const [graduationYear, setGraduationYear] = useState("");
  const [suggestions, setSuggestions] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const studyHabits = [
    "Making flashcards",
    "Teaching the material to others",
    "Attending teacher consultations",
    "Creating summary notes",
    "Reviewing regularly",
    "Practice problems",
    "Group study sessions"
  ];

  const generateGraduationYears = () => {
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    const baseYear = currentMonth >= 7 ? currentYear + 1 : currentYear;
    return Array.from({length: 4}, (_, i) => baseYear + i);
  };

  const handleAnalyze = async(e) => {
    setLoading(true);
    setError(null);
    setFeedback(null);
    e.preventDefault();
    const formData = new FormData();
    formData.append("file", reportCard);
    formData.append("student_id", studentID);
    formData.append("graduation_year", graduationYear);

    if (!reportCard) {
      setError("Please upload a PDF file");
      setLoading(false);
      return;
    }
   
    try {
      const response = await axios.post("http://127.0.0.1:5000/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        }
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

  {
    //handleHabits
  }

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
      <h1 style={{ color: "#e60000", marginBottom: "20px" }}>Interim Comments Analysis</h1>
      <input
        type="file"
        value={reportCard}
        accept="pdf"
        onChange={(e) => setReportCard(e.target.files[0])}
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

      {
        // input student id
      }
      <h1 style={{color: "#e60000", marginBottom: "20px"}}>Student ID: </h1>
      <input type="text" value={studentID} onChange={(e) => setStudentID(e.target.value)} required></input>

      {
        // select dropdown graduation year
      }
      <h1 style={{color: "#e60000", marginBottom: "20px"}}>Graduation Year: </h1>
      <select value={graduationYear} onChange={(e) => setGraduationYear(e.target.value)} required>
        <option value="">Select Year</option>
        {generateGraduationYears().map(year => (
          <option key={year} value={year}>{year}</option>
        ))}
      </select>

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
          <h3 style={{ color: "#e60000" }}>AI Analysis</h3>
          <h4><strong>Strengths:</strong></h4>
          <ul>
            {feedback.strengths.map((strength, index) => (
              <li key={index}>{strength}</li>
            ))}
          </ul>
          <h4><strong>Areas for Improvement:</strong></h4>
          <ul>
            {feedback.areas_for_improvement.map((area, index) => (
              <li key={index}>{area}</li>
            ))}
          </ul>
          <h4><strong>Progress from Previous Years:</strong></h4>
          <p>{historical_analysis}</p>
          
          

        </div> 
        
      )}
    </div>
  );
}

export default App;
