export const sendMessage = async (userId, message) => {
  const res = await fetch("http://localhost:8000/api/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, message })
  });
  const data = await res.json();
  return data.response;
};

