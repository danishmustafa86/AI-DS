export const sendMessage = async (userId, message) => {
  try {
    const res = await fetch("http://localhost:8000/api/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, message }),
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();
    return data.response;
  } catch (err) {
    console.error("❌ API call failed:", err);
    return "Sorry, the assistant is currently unavailable.";
  }
};
