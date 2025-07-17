import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("http://localhost:5000/api/hello")
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => setMessage("Failed to connect to backend."));
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold text-blue-600">Student Life Organiser</h1>
      <p className="mt-2 text-gray-700">{message}</p>
    </div>
  );
}

export default App;
