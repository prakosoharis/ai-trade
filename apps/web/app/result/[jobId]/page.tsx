"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/api";

type Score = {
  component: string;
  score: number;
  weight: number;
  bias: string;
  summary: string;
  evidence: string[];
  risks: string[];
};

type Result = {
  symbol: string;
  timeframe: string;
  final_view: string;
  decision: string;
  confidence_score: number;
  risk_level: string;
  market_regime: string;
  current_price: number;
  entry_low: number;
  entry_high: number;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2: number;
  take_profit_3: number;
  risk_reward_ratio: number;
  executive_summary: string;
  thesis: string;
  invalidation: string;
  holding_horizon: string;
  score_breakdown: Score[];
  detail_sections: any;
};

export default function ResultPage({ params }: { params: { jobId: string } }) {
  const [result, setResult] = useState<Result | null>(null);
  const [open, setOpen] = useState<string | null>("Technical");

  useEffect(() => {
    apiGet<Result>(`/api/analysis/${params.jobId}/result`).then(setResult);
  }, [params.jobId]);

  if (!result) {
    return <main className="container"><div className="card" style={{marginTop: 38}}>Loading result...</div></main>;
  }

  return (
    <main className="container">
      <section className="card result-header">
        <div className="result-title">
          <div className="logo">↗</div>
          <div>
            <h2 style={{margin: 0}}>{result.symbol}</h2>
            <div className="muted">{result.timeframe.toUpperCase()} · {result.current_price.toLocaleString()} · {result.market_regime}</div>
          </div>
        </div>
        <div style={{textAlign: "right"}}>
          <div className="muted">Confidence</div>
          <div className="score-big">{result.confidence_score}/100</div>
        </div>
        <Link href="/analysis"><button className="button secondary">New Analysis</button></Link>
      </section>

      <section className="grid-2">
        <div>
          <div className="chart-placeholder">
            <div className="chart-line" />
          </div>
          <div className="card" style={{marginTop: 18}}>
            <div className="label">Executive Summary</div>
            <p style={{lineHeight: 1.7}}>{result.executive_summary}</p>
          </div>

          <div className="card" style={{marginTop: 18}}>
            <div className="label">Decision Framework</div>
            <h2 style={{marginBottom: 0}}>{result.decision}</h2>
            <p className="muted">{result.thesis}</p>
          </div>

          <div className="card" style={{marginTop: 18}}>
            <div className="label">Score Breakdown — Click to inspect detail</div>
            <div className="breakdown" style={{marginTop: 14}}>
              {result.score_breakdown.map(item => (
                <div
                  key={item.component}
                  className="breakdown-row"
                  onClick={() => setOpen(open === item.component ? null : item.component)}
                  style={{cursor: "pointer"}}
                >
                  <div className="breakdown-top">
                    <div>
                      <strong>{item.component}</strong>
                      <div className="muted">Weight {item.weight}% · {item.bias}</div>
                    </div>
                    <div className="score-big" style={{fontSize: 24}}>{item.score}</div>
                  </div>
                  <div className="progress">
                    <div className="progress-fill" style={{width: `${item.score}%`}} />
                  </div>
                  {open === item.component && (
                    <div style={{marginTop: 14}}>
                      <p>{item.summary}</p>
                      <div className="grid-2">
                        <div>
                          <div className="label">Evidence</div>
                          <ul>
                            {item.evidence.map((e, i) => <li key={i}>{e}</li>)}
                          </ul>
                        </div>
                        <div>
                          <div className="label">Risks</div>
                          <ul>
                            {item.risks.map((r, i) => <li key={i}>{r}</li>)}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <aside>
          <div className="card">
            <div className="label">Final View</div>
            <h2>{result.final_view}</h2>
            <p className="muted">Risk level: {result.risk_level}</p>
          </div>

          <div className="card" style={{marginTop: 18}}>
            <div className="label">Trade Setup</div>
            <div className="grid-2" style={{gridTemplateColumns: "1fr 1fr", gap: 10}}>
              <div className="metric"><div className="label">Entry Low</div><div className="metric-value">{result.entry_low.toLocaleString(undefined, {maximumFractionDigits: 2})}</div></div>
              <div className="metric"><div className="label">Entry High</div><div className="metric-value">{result.entry_high.toLocaleString(undefined, {maximumFractionDigits: 2})}</div></div>
              <div className="metric"><div className="label">Stop Loss</div><div className="metric-value red">{result.stop_loss.toLocaleString(undefined, {maximumFractionDigits: 2})}</div></div>
              <div className="metric"><div className="label">R:R</div><div className="metric-value green">{result.risk_reward_ratio}:1</div></div>
              <div className="metric"><div className="label">TP1</div><div className="metric-value green">{result.take_profit_1.toLocaleString(undefined, {maximumFractionDigits: 2})}</div></div>
              <div className="metric"><div className="label">TP2</div><div className="metric-value green">{result.take_profit_2.toLocaleString(undefined, {maximumFractionDigits: 2})}</div></div>
            </div>
          </div>

          <div className="card" style={{marginTop: 18}}>
            <div className="label">Risk & Invalidation</div>
            <p>{result.invalidation}</p>
          </div>

          <div className="card" style={{marginTop: 18}}>
            <div className="label">Methodology</div>
            <p className="muted">
              Rule-based weighted scoring + structured research framework. ML and real LLM research generation are planned for later phases.
            </p>
          </div>
        </aside>
      </section>
    </main>
  );
}
