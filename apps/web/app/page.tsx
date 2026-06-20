import Link from "next/link";

export default function Home() {
  return (
    <main>
      <section className="hero container">
        <div className="badge">● Live Analysis Engine</div>
        <h1>Hedge Fund–Grade<br /><span>Market Research</span></h1>
        <p>
          Pre-MVP institutional research workbench: select an asset, run a research pipeline,
          and receive a structured decision summary with scoring, risk, and trade plan.
        </p>
        <div style={{maxWidth: 360, margin: "28px auto 0"}}>
          <Link href="/analysis"><button className="button">Run Institutional Analysis</button></Link>
        </div>
      </section>
    </main>
  );
}
