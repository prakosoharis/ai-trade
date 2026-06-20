"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

type Intelligence = {
  market_regime: string;
  summary: string;
  top_opportunities: {symbol: string; view: string; confidence: number}[];
  risk_events: string[];
};

export default function IntelligencePage() {
  const [data, setData] = useState<Intelligence | null>(null);

  useEffect(() => {
    apiGet<Intelligence>("/api/intelligence").then(setData);
  }, []);

  return (
    <main className="container">
      <section className="hero">
        <div className="badge">Intelligence</div>
        <h1>Daily Market <span>Brief</span></h1>
        <p>Pre-MVP intelligence page with mock/hybrid market brief and opportunity list.</p>
      </section>

      <section className="grid-2">
        <div className="card">
          <div className="label">Market Regime</div>
          <h2>{data?.market_regime || "Loading..."}</h2>
          <p className="muted">{data?.summary}</p>
        </div>

        <div className="card">
          <div className="label">Risk Events</div>
          <ul>
            {data?.risk_events.map((x) => <li key={x}>{x}</li>)}
          </ul>
        </div>
      </section>

      <section className="card" style={{marginTop: 18}}>
        <div className="label">Top Opportunities</div>
        <div className="grid-3" style={{marginTop: 14}}>
          {data?.top_opportunities.map(item => (
            <div key={item.symbol} className="metric">
              <div className="label">{item.symbol}</div>
              <div className="metric-value">{item.confidence}/100</div>
              <p className="muted">{item.view}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
