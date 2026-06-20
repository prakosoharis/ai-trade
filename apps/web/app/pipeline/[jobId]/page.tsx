"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet } from "@/lib/api";

type Job = {
  id: string;
  symbol: string;
  timeframe: string;
  price: number;
  status: string;
  current_step: number;
  progress_percent: number;
  created_at: string;
  failed_reason?: string;
};

type Step = {
  id: string;
  step_order: number;
  step_name: string;
  status: string;
  output_summary?: string;
};

export default function PipelinePage({ params }: { params: { jobId: string } }) {
  const router = useRouter();
  const [job, setJob] = useState<Job | null>(null);
  const [steps, setSteps] = useState<Step[]>([]);

  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        const j = await apiGet<Job>(`/api/analysis/${params.jobId}`);
        const s = await apiGet<{steps: Step[]}>(`/api/analysis/${params.jobId}/steps`);
        setJob(j);
        setSteps(s.steps);
        if (j.status === "completed") {
          router.push(`/result/${params.jobId}`);
        }
      } catch (err) {
        console.error(err);
      }
    }, 900);

    return () => clearInterval(timer);
  }, [params.jobId, router]);

  return (
    <main className="container">
      <section className="card" style={{marginTop: 38}}>
        <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
          <div>
            <div style={{fontWeight: 900}}>Generating research note for <span className="green">{job?.symbol || "..."}</span></div>
            <div className="muted">{job?.timeframe?.toUpperCase()} · {job?.price?.toLocaleString()} · status: {job?.status || "loading"}</div>
          </div>
          <div className="score-big">{job?.progress_percent || 0}%</div>
        </div>
      </section>

      <section className="pipeline-layout">
        <div className="card">
          <div className="label">Research Pipeline</div>
          <div style={{marginTop: 18}}>
            {steps.map(step => (
              <div key={step.id} className={`step ${step.status}`}>
                <div className="step-dot" />
                <div>
                  <div>{step.step_name}</div>
                  {step.status === "running" && <div className="green" style={{fontSize: 12}}>Running...</div>}
                  {step.status === "completed" && <div className="muted" style={{fontSize: 12}}>Completed</div>}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="label">Research Engine</div>
          <h2 style={{marginTop: 14}}>Connecting to research engine...</h2>
          <p className="muted">
            The worker is processing the analysis asynchronously. This pre-MVP uses deterministic scoring and mock/hybrid market data.
          </p>
          <div className="progress">
            <div className="progress-fill" style={{width: `${job?.progress_percent || 0}%`}} />
          </div>
          {job?.status === "failed" && <p className="red">Failed: {job.failed_reason}</p>}
        </div>
      </section>
    </main>
  );
}
