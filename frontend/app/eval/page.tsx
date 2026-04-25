"use client";

import { useState } from "react";

const api = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function EvalPage() {
  const [report, setReport] = useState<any>(null);
  const [tune, setTune] = useState<any>(null);
  const [benchmark, setBenchmark] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadReport() {
    const res = await fetch(`${api}/api/v1/eval/report`);
    setReport(await res.json());
  }

  async function runTune() {
    const res = await fetch(`${api}/api/v1/meta/tune`, { method: "POST" });
    setTune(await res.json());
  }

  async function loadBenchmark() {
    setError(null);
    const res = await fetch(`${api}/api/v1/eval/benchmark`);
    const data = await res.json();
    if (!res.ok) {
      setError(data?.error?.message ?? "Failed to load benchmark report.");
      return;
    }
    setBenchmark(data);
  }

  return (
    <main>
      <h2>Evaluation & Meta Tuner</h2>
      <button onClick={loadReport}>Load Eval Report</button>
      <button onClick={runTune}>Run Meta Tune</button>
      <button onClick={loadBenchmark}>Load Benchmark Report</button>
      <pre>{report ? JSON.stringify(report, null, 2) : "No report loaded."}</pre>
      <pre>{tune ? JSON.stringify(tune, null, 2) : "No tuning yet."}</pre>
      <pre>{benchmark ? JSON.stringify(benchmark, null, 2) : "No benchmark loaded."}</pre>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
    </main>
  );
}
