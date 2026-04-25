"use client";

import { FormEvent, useState } from "react";

const api = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function AskPage() {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  const [confidence, setConfidence] = useState<number | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    const res = await fetch(`${api}/api/v1/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, use_knowledge: true })
    });
    const data = await res.json();
    setAnswer(data.answer);
    setConfidence(data.confidence);
  }

  return (
    <main>
      <h2>Ask Runtime</h2>
      <form onSubmit={submit}>
        <input value={message} onChange={(e) => setMessage(e.target.value)} style={{ width: 520 }} />
        <button type="submit">Ask</button>
      </form>
      <p><strong>Confidence:</strong> {confidence ?? "N/A"}</p>
      <pre>{answer}</pre>
    </main>
  );
}
