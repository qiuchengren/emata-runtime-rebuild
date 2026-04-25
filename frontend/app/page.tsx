import Link from "next/link";

export default function Home() {
  return (
    <main>
      <h1>EMATA Runtime Rebuild</h1>
      <p>Replica + innovation: Ask Runtime, Knowledge ingestion, Auto Eval, Meta Tuner.</p>
      <ul>
        <li><Link href="/ask">Ask Runtime</Link></li>
        <li><Link href="/knowledge">Knowledge Upload</Link></li>
        <li><Link href="/eval">Evaluation Dashboard</Link></li>
      </ul>
    </main>
  );
}
