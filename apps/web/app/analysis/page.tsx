"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost } from "@/lib/api";

type Asset = {
  symbol: string;
  name: string;
  asset_class: string;
  price: number;
  change_pct: number;
};

type Timeframe = {
  value: string;
  label: string;
};

export default function AnalysisPage() {
  const router = useRouter();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [timeframes, setTimeframes] = useState<Timeframe[]>([]);
  const [assetClass, setAssetClass] = useState("Crypto");
  const [selected, setSelected] = useState<Asset | null>(null);
  const [customSymbol, setCustomSymbol] = useState("");
  const [price, setPrice] = useState<number>(0);
  const [timeframe, setTimeframe] = useState("1d");
  const [context, setContext] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiGet<{assets: Asset[]; timeframes: Timeframe[]}>("/api/assets").then((data) => {
      setAssets(data.assets);
      setTimeframes(data.timeframes);
      const btc = data.assets.find(a => a.symbol === "BTCUSD") || data.assets[0];
      setSelected(btc);
      setAssetClass(btc.asset_class);
      setPrice(btc.price);
    });
  }, []);

  const assetClasses = useMemo(() => Array.from(new Set(assets.map(a => a.asset_class))), [assets]);
  const filtered = assets.filter(a => a.asset_class === assetClass);

  async function runAnalysis() {
    const symbol = (customSymbol || selected?.symbol || "BTCUSD").toUpperCase();
    const selectedAssetClass = selected?.asset_class || assetClass;

    setLoading(true);
    try {
      const res = await apiPost<{job_id: string}>("/api/analysis", {
        symbol,
        asset_class: selectedAssetClass,
        timeframe,
        price,
        additional_context: context
      });
      router.push(`/pipeline/${res.job_id}`);
    } catch (err) {
      alert("Failed to create analysis job. Please check API logs.");
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <section className="hero">
        <div className="badge">● Live Analysis Engine</div>
        <h1>Hedge Fund–Grade<br /><span>Market Research</span></h1>
        <p>Top-down macro → fundamental drivers → technical analysis → quantitative scoring → risk plan.</p>
      </section>

      <section className="card">
        <div className="tabs">
          {assetClasses.map(cls => (
            <button
              key={cls}
              className={`tab ${assetClass === cls ? "active" : ""}`}
              onClick={() => {
                setAssetClass(cls);
                const first = assets.find(a => a.asset_class === cls);
                if (first) {
                  setSelected(first);
                  setPrice(first.price);
                  setCustomSymbol("");
                }
              }}
            >
              {cls}
            </button>
          ))}
        </div>

        <div className="asset-grid">
          {filtered.slice(0, 6).map(asset => (
            <div
              key={asset.symbol}
              className={`asset-card ${selected?.symbol === asset.symbol ? "active" : ""}`}
              onClick={() => {
                setSelected(asset);
                setPrice(asset.price);
                setCustomSymbol("");
              }}
            >
              <div className="asset-symbol">{asset.symbol}</div>
              <div className="asset-name">{asset.name}</div>
            </div>
          ))}
        </div>

        <div style={{marginTop: 16}}>
          <input
            className="input"
            placeholder="Or type custom symbol, e.g. GBPJPY, CORN, SILVER..."
            value={customSymbol}
            onChange={e => setCustomSymbol(e.target.value)}
          />
        </div>

        <div className="form-grid">
          <div className="price-card">
            <div className="label">{customSymbol || selected?.symbol || "Asset"} — Live Price</div>
            <div className="price">{price.toLocaleString(undefined, { maximumFractionDigits: 4 })}</div>
            <div className="muted">
              Change: <span className={(selected?.change_pct || 0) >= 0 ? "green" : "red"}>{selected?.change_pct ?? 0}%</span> · mock/hybrid feed
            </div>
          </div>

          <div className="field">
            <label className="label">Price Override</label>
            <input
              type="number"
              className="input"
              value={price}
              onChange={e => setPrice(Number(e.target.value))}
            />
            <label className="label">Primary Timeframe</label>
            <select className="select" value={timeframe} onChange={e => setTimeframe(e.target.value)}>
              {timeframes.map(tf => <option key={tf.value} value={tf.value}>{tf.label}</option>)}
            </select>
          </div>
        </div>

        <div style={{marginTop: 18}} className="field">
          <label className="label">Additional Context Optional</label>
          <textarea
            className="textarea"
            placeholder="e.g. Recent price rejected from weekly resistance, Fed meeting tomorrow, liquidity sweep observed..."
            value={context}
            onChange={e => setContext(e.target.value)}
          />
        </div>

        <div style={{marginTop: 18}}>
          <button className="button" onClick={runAnalysis} disabled={loading || !price}>
            {loading ? "Creating Analysis Job..." : `Run Institutional Analysis — ${(customSymbol || selected?.symbol || "Asset").toUpperCase()}`}
          </button>
        </div>
      </section>
    </main>
  );
}
