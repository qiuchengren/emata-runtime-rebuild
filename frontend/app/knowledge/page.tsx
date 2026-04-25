"use client";

import { FormEvent, useState } from "react";

const api = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function KnowledgePage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState("");

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${api}/api/v1/knowledge/uploads`, { method: "POST", body: form });
    const data = await res.json();
    setResult(`${data.doc_id} - chunks: ${data.chunks}`);
  }

  return (
    <main>
      <h2>Knowledge Upload</h2>
      <form onSubmit={submit}>
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <button type="submit">Upload</button>
      </form>
      <p>{result}</p>
    </main>
  );
}
