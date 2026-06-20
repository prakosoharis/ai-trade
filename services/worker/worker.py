import os
import json
import time
import uuid
import hashlib
from datetime import datetime, timezone
from decimal import Decimal

import psycopg2
import psycopg2.extras
import redis


POSTGRES_DB = os.getenv("POSTGRES_DB", "airesearch")
POSTGRES_USER = os.getenv("POSTGRES_USER", "airesearch")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airesearch")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

QUEUE_NAME = "analysis_jobs"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def db_conn():
    return psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )


def rds():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def fetch_one(sql, params=()):
    with db_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return rows[0] if rows else None


def execute(sql, params=()):
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)


def stable_int(key: str, min_value: int, max_value: int) -> int:
    digest = hashlib.sha256(key.encode()).hexdigest()
    num = int(digest[:8], 16)
    return min_value + (num % (max_value - min_value + 1))


def get_weights(timeframe: str):
    if timeframe in ["5m", "15m"]:
        return {
            "Technical": 30,
            "Volume / Order Flow": 25,
            "Quantitative": 20,
            "News / Sentiment": 10,
            "Macro": 5,
            "Fundamental": 5,
            "Cross-Asset": 5,
        }
    if timeframe in ["1h", "4h"]:
        return {
            "Technical": 28,
            "Volume / Order Flow": 18,
            "Quantitative": 18,
            "Macro": 12,
            "Fundamental": 10,
            "Cross-Asset": 8,
            "News / Sentiment": 6,
        }
    if timeframe == "1w":
        return {
            "Macro": 30,
            "Fundamental": 25,
            "Cross-Asset": 15,
            "Technical": 15,
            "Quantitative": 10,
            "News / Sentiment": 5,
            "Volume / Order Flow": 0,
        }
    return {
        "Macro": 20,
        "Fundamental": 15,
        "Technical": 25,
        "Quantitative": 15,
        "Cross-Asset": 10,
        "News / Sentiment": 10,
        "Volume / Order Flow": 5,
    }


def build_result(job):
    symbol = job["symbol"]
    timeframe = job["timeframe"]
    price = float(job["price"])
    weights = get_weights(timeframe)

    components = []
    total = 0
    weight_total = 0

    bias_map = {
        "Macro": "Supportive",
        "Fundamental": "Mild bullish",
        "Technical": "Bullish",
        "Volume / Order Flow": "Constructive",
        "Quantitative": "Positive",
        "News / Sentiment": "Neutral positive",
        "Cross-Asset": "Supportive",
    }

    for component, weight in weights.items():
        if weight <= 0:
            score = 50
        else:
            score = stable_int(f"{symbol}-{timeframe}-{component}", 58, 88)
        total += score * weight
        weight_total += weight
        components.append({
            "component": component,
            "score": score,
            "weight": weight,
            "bias": bias_map.get(component, "Neutral"),
            "summary": f"{component} conditions are {bias_map.get(component, 'neutral').lower()} for {symbol} on the selected horizon.",
            "evidence": [
                f"{component} signal is aligned with the selected {timeframe} horizon.",
                "Current setup is evaluated using a transparent rule-based scoring framework.",
                "This is mock/hybrid data for pre-MVP validation."
            ],
            "risks": [
                "Market conditions can change quickly.",
                "Signal should be invalidated if price breaks the defined risk level."
            ],
        })

    confidence = int(round(total / max(weight_total, 1)))
    final_view = "Bullish Tactical Setup" if confidence >= 70 else "Neutral / Wait for Confirmation"
    decision = "Buy on Pullback" if confidence >= 70 else "Wait"
    risk_level = "Medium-High" if confidence >= 75 else "Medium"
    market_regime = "Risk-on momentum with elevated volatility" if confidence >= 70 else "Mixed regime"

    # Basic trade plan
    entry_low = price * 0.982
    entry_high = price * 1.005
    stop_loss = price * 0.95
    tp1 = price * 1.06
    tp2 = price * 1.095
    tp3 = price * 1.14
    risk = max(price - stop_loss, 0.0001)
    reward = tp2 - price
    rr = round(reward / risk, 2)

    executive_summary = (
        f"{symbol} currently presents a {final_view.lower()} with a {confidence}/100 conviction score. "
        f"The decision framework favors {decision.lower()} rather than chasing price. "
        f"The setup is supported by technical structure, macro context, and quantitative confluence, "
        f"while risk remains {risk_level.lower()} due to volatility and invalidation sensitivity."
    )

    thesis = (
        f"The core thesis is that {symbol} has enough multi-factor support to justify tactical consideration, "
        f"provided price remains above the invalidation zone. The strongest factors are visible in the score breakdown; "
        f"users should inspect each module before making a decision."
    )

    invalidation = (
        f"The bullish thesis is invalidated if {symbol} closes below approximately {stop_loss:,.2f} "
        f"on the selected {timeframe} timeframe or if macro/news conditions shift materially against the asset."
    )

    holding_map = {
        "5m": "Scalp",
        "15m": "Intraday",
        "1h": "Intraday Swing",
        "4h": "Swing",
        "1d": "Position",
        "1w": "Macro",
    }

    detail_sections = {
        "methodology": {
            "title": "Methodology",
            "content": "The result is generated from a transparent weighted scoring engine. The LLM layer is not required in this pre-MVP version; current narrative is template-based for validation."
        },
        "risk": {
            "title": "Risk & Invalidation",
            "content": invalidation
        },
        "trade_plan": {
            "title": "Trade Plan",
            "content": f"Entry zone {entry_low:,.2f}–{entry_high:,.2f}, stop loss {stop_loss:,.2f}, TP1 {tp1:,.2f}, TP2 {tp2:,.2f}, TP3 {tp3:,.2f}. Risk/reward around {rr}:1."
        }
    }

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "final_view": final_view,
        "decision": decision,
        "confidence_score": confidence,
        "risk_level": risk_level,
        "market_regime": market_regime,
        "current_price": price,
        "entry_low": entry_low,
        "entry_high": entry_high,
        "stop_loss": stop_loss,
        "take_profit_1": tp1,
        "take_profit_2": tp2,
        "take_profit_3": tp3,
        "risk_reward_ratio": rr,
        "executive_summary": executive_summary,
        "thesis": thesis,
        "invalidation": invalidation,
        "holding_horizon": holding_map.get(timeframe, "Position"),
        "score_breakdown": components,
        "detail_sections": detail_sections,
    }


def process_job(job_id: str):
    print(f"Processing job {job_id}", flush=True)
    job = fetch_one("SELECT * FROM analysis_jobs WHERE id = %s", (job_id,))
    if not job:
        print(f"Job {job_id} not found", flush=True)
        return

    try:
        execute(
            "UPDATE analysis_jobs SET status='running', started_at=%s, progress_percent=1 WHERE id=%s",
            (now_iso(), job_id),
        )

        steps = []
        with db_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM analysis_pipeline_steps WHERE analysis_job_id=%s ORDER BY step_order",
                    (job_id,),
                )
                steps = cur.fetchall()

        total_steps = len(steps)
        for i, step in enumerate(steps, start=1):
            execute(
                """
                UPDATE analysis_pipeline_steps
                SET status='running', started_at=%s
                WHERE id=%s
                """,
                (now_iso(), step["id"]),
            )
            execute(
                """
                UPDATE analysis_jobs
                SET current_step=%s, progress_percent=%s
                WHERE id=%s
                """,
                (i, int(((i - 1) / total_steps) * 100), job_id),
            )

            time.sleep(0.7)

            summary = f"Completed: {step['step_name']} for {job['symbol']}."
            execute(
                """
                UPDATE analysis_pipeline_steps
                SET status='completed', completed_at=%s, output_summary=%s
                WHERE id=%s
                """,
                (now_iso(), summary, step["id"]),
            )

        result = build_result(job)

        execute(
            """
            INSERT INTO research_results (
                id, analysis_job_id, symbol, timeframe, final_view, decision,
                confidence_score, risk_level, market_regime, current_price,
                entry_low, entry_high, stop_loss, take_profit_1, take_profit_2, take_profit_3,
                risk_reward_ratio, executive_summary, thesis, invalidation, holding_horizon,
                score_breakdown, detail_sections, created_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            )
            """,
            (
                str(uuid.uuid4()), job_id, result["symbol"], result["timeframe"],
                result["final_view"], result["decision"], result["confidence_score"],
                result["risk_level"], result["market_regime"], result["current_price"],
                result["entry_low"], result["entry_high"], result["stop_loss"],
                result["take_profit_1"], result["take_profit_2"], result["take_profit_3"],
                result["risk_reward_ratio"], result["executive_summary"], result["thesis"],
                result["invalidation"], result["holding_horizon"],
                json.dumps(result["score_breakdown"]), json.dumps(result["detail_sections"]),
                now_iso(),
            ),
        )

        execute(
            """
            UPDATE analysis_jobs
            SET status='completed', progress_percent=100, completed_at=%s
            WHERE id=%s
            """,
            (now_iso(), job_id),
        )

        execute(
            """
            INSERT INTO audit_logs(id, entity_type, entity_id, action, payload, created_at)
            VALUES (%s, 'analysis_job', %s, 'completed', %s, %s)
            """,
            (
                str(uuid.uuid4()),
                job_id,
                json.dumps({"confidence_score": result["confidence_score"], "decision": result["decision"]}),
                now_iso(),
            ),
        )

        print(f"Completed job {job_id}", flush=True)

    except Exception as exc:
        print(f"Failed job {job_id}: {exc}", flush=True)
        execute(
            "UPDATE analysis_jobs SET status='failed', failed_reason=%s, completed_at=%s WHERE id=%s",
            (str(exc), now_iso(), job_id),
        )


def main():
    print("Research worker started", flush=True)
    client = rds()

    while True:
        try:
            item = client.brpop(QUEUE_NAME, timeout=5)
            if not item:
                continue
            _, job_id = item
            process_job(job_id)
        except Exception as exc:
            print(f"Worker loop error: {exc}", flush=True)
            time.sleep(2)


if __name__ == "__main__":
    main()
