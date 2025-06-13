// src/utils/api.js
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000', // Your FastAPI server
});

export const sendMessage = async (message) => {
  const response = await API.post('/chat', { message });
  return response.data.response;
};
