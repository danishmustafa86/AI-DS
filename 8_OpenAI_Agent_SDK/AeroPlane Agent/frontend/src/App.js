import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [responses, setResponses] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setResponses((prev) => [...prev, { role: "user", message: prompt }]);

    try {
      const res = await axios.post("http://127.0.0.1:8000/chat", { prompt });
      setResponses((prev) => [...prev, { role: "agent", message: res.data.response }]);
    } catch (err) {
      setResponses((prev) => [
        ...prev,
        { role: "agent", message: "❌ Error getting response from server." },
      ]);
    }

    setPrompt("");
  };

  return (
    <div className="App">
      <h1>✈️ Airline Agent Chat</h1>
      <div className="chat-box">
        {responses.map((msg, index) => (
          <div
            key={index}
            className={msg.role === "user" ? "chat-message user" : "chat-message agent"}
          >
            <strong>{msg.role === "user" ? "You" : "Agent"}:</strong> {msg.message}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default App;
