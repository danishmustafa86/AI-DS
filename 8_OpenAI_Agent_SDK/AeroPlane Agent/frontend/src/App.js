import { useState } from 'react';
import { sendMessage } from './api';
import { v4 as uuidv4 } from 'uuid';

function App() {
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);
  const [userId] = useState(uuidv4());

  const handleSubmit = async (e) => {
    e.preventDefault();
    const userMessage = input;
    setChat([...chat, { role: 'user', content: userMessage }]);
    setInput("");
    const response = await sendMessage(userId, userMessage);
    setChat([...chat, { role: 'user', content: userMessage }, { role: 'agent', content: response }]);
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Airline Assistant</h1>
      <div style={{ height: 400, overflowY: 'scroll', border: '1px solid gray', padding: 10 }}>
        {chat.map((msg, index) => (
          <div key={index}><b>{msg.role}:</b> {msg.content}</div>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Enter message" />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default App;
