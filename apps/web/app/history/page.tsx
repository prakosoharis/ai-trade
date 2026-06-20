"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/api";

type HistoryItem = {
  job_id: string;
  symbol: string;
  asset_class: string;
  timeframe: string;
  status: string;
  created_at: string;
  final_view?: string;
  decision?: string;
  confidence_score?: number;
  risk_level?: string;
};

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);

  useEffect(() => {
    apiGet<{items: HistoryItem[]}>("/api/history").then(data => setItems(data.items));
  }, []);

  return (
    <main className="container">
      <section className="hero">
        <div className="badge">History</div>
        <h1>Previous <span>Research Notes</span></h1>
        <p>Every analysis request is saved here for review, traceability, and demo continuity.</p>
      </section>

      <section className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Asset</th>
              <th>Timeframe</th>
              <th>Status</th>
              <th>Decision</th>
              <th>Confidence</th>
              <th>Created</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.job_id}>
                <td><strong>{item.symbol}</strong><div className="muted">{item.asset_class}</div></td>
                <td>{item.timeframe?.toUpperCase()}</td>
                <td>{item.status}</td>
                <td>{item.decision || "-"}</td>
                <td>{item.confidence_score ? `${item.confidence_score}/100` : "-"}</td>
                <td>{new Date(item.created_at).toLocaleString()}</td>
                <td>
                  {item.status === "completed" ? (
                    <Link className="green" href={`/result/${item.job_id}`}>Open</Link>
                  ) : (
                    <Link className="muted" href={`/pipeline/${item.job_id}`}>Pipeline</Link>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 0 && <p className="muted">No history yet. Run an analysis first.</p>}
      </section>
    </main>
  );
}
