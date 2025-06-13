// src/components/ChatBox.js
import React, { useState } from 'react';
import { sendMessage } from '../utils/api';

const ChatBox = () => {
  const [input, setInput] = useState('');
  const [chat, setChat] = useState([]);

  const handleSend = async () => {
    if (!input) return;
    const reply = await sendMessage(input);
    setChat([...chat, `You: ${input}`, `Agent: ${reply}`]);
    setInput('');
  };

  return (
    <div style={{ padding: 20, maxWidth: 600, margin: 'auto' }}>
      <h2>✈️ Airline Assistant</h2>
      <div style={{ backgroundColor: '#f0f0f0', padding: 10, height: 300, overflowY: 'scroll' }}>
        {chat.map((msg, idx) => (
          <div key={idx}>{msg}</div>
        ))}
      </div>
      <div style={{ marginTop: 10 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{ width: '80%', padding: 5 }}
          placeholder="Ask your question..."
        />
        <button onClick={handleSend} style={{ padding: 5, marginLeft: 5 }}>Send</button>
      </div>
    </div>
  );
};

export default ChatBox;
