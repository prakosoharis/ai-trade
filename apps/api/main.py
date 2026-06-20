import os
import json
import uuid
import time
from datetime import datetime, timezone
from typing import Optional, Any

import psycopg2
import psycopg2.extras
import redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


POSTGRES_DB = os.getenv("POSTGRES_DB", "airesearch")
POSTGRES_USER = os.getenv("POSTGRES_USER", "airesearch")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airesearch")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

QUEUE_NAME = "analysis_jobs"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def db_conn():
    return psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )


def redis_client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def execute(sql: str, params: tuple = (), fetch: bool = False):
    with db_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            if fetch:
                return cur.fetchall()
            return None


def execute_one(sql: str, params: tuple = ()):
    rows = execute(sql, params, fetch=True)
    return rows[0] if rows else None


PIPELINE_STEPS = [
    "Assessing macro regime",
    "Evaluating fundamental drivers",
    "Reading market structure",
    "Scanning technical signals",
    "Analysing volume, order flow & institutional positioning",
    "Running quantitative factors",
    "Mapping intermarket correlations & cross-asset signals",
    "Calculating multi-factor confluence & conviction score",
    "Assessing risk, invalidation & downside scenario",
    "Building trade plan & position sizing framework",
    "Generating final research note & decision summary",
]


ASSETS = [
    {"symbol": "BTCUSD", "name": "Bitcoin", "asset_class": "Crypto", "price": 63159.15, "change_pct": -4.72},
    {"symbol": "ETHUSD", "name": "Ethereum", "asset_class": "Crypto", "price": 3380.20, "change_pct": -2.18},
    {"symbol": "SOLUSD", "name": "Solana", "asset_class": "Crypto", "price": 142.40, "change_pct": 1.21},
    {"symbol": "XAUUSD", "name": "Gold", "asset_class": "Commodities", "price": 2580.25, "change_pct": 0.84},
    {"symbol": "XAGUSD", "name": "Silver", "asset_class": "Commodities", "price": 30.12, "change_pct": 0.31},
    {"symbol": "WTI", "name": "WTI Oil", "asset_class": "Commodities", "price": 76.45, "change_pct": -1.10},
    {"symbol": "BRENT", "name": "Brent Oil", "asset_class": "Commodities", "price": 80.22, "change_pct": -0.90},
    {"symbol": "EURUSD", "name": "Euro / US Dollar", "asset_class": "Forex", "price": 1.0862, "change_pct": 0.18},
    {"symbol": "GBPUSD", "name": "British Pound / US Dollar", "asset_class": "Forex", "price": 1.2711, "change_pct": 0.12},
    {"symbol": "USDJPY", "name": "US Dollar / Japanese Yen", "asset_class": "Forex", "price": 156.42, "change_pct": -0.21},
    {"symbol": "NASDAQ", "name": "Nasdaq 100", "asset_class": "Indices", "price": 19750.32, "change_pct": 0.65},
    {"symbol": "SPX", "name": "S&P 500", "asset_class": "Indices", "price": 5525.12, "change_pct": 0.38},
    {"symbol": "AAPL", "name": "Apple", "asset_class": "Stocks", "price": 212.52, "change_pct": 1.15},
    {"symbol": "NVDA", "name": "NVIDIA", "asset_class": "Stocks", "price": 128.70, "change_pct": 2.41},
    {"symbol": "US10Y", "name": "US 10Y Yield", "asset_class": "Bonds", "price": 4.28, "change_pct": -0.03},
]


TIMEFRAMES = [
    {"value": "5m", "label": "5 minutes — Scalp"},
    {"value": "15m", "label": "15 minutes — Intraday"},
    {"value": "1h", "label": "1 hour — Intraday Swing"},
    {"value": "4h", "label": "4 hours — Swing"},
    {"value": "1d", "label": "Daily — Position"},
    {"value": "1w", "label": "Weekly — Macro"},
]


def init_db():
    schema = """
    CREATE TABLE IF NOT EXISTS assets (
        symbol TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        asset_class TEXT NOT NULL,
        price NUMERIC NOT NULL,
        change_pct NUMERIC NOT NULL DEFAULT 0,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS analysis_jobs (
        id UUID PRIMARY KEY,
        symbol TEXT NOT NULL,
        asset_class TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        price NUMERIC NOT NULL,
        additional_context TEXT,
        status TEXT NOT NULL,
        current_step INTEGER NOT NULL DEFAULT 0,
        progress_percent INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL,
        started_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ,
        failed_reason TEXT
    );

    CREATE TABLE IF NOT EXISTS analysis_pipeline_steps (
        id UUID PRIMARY KEY,
        analysis_job_id UUID NOT NULL REFERENCES analysis_jobs(id) ON DELETE CASCADE,
        step_order INTEGER NOT NULL,
        step_name TEXT NOT NULL,
        status TEXT NOT NULL,
        output_summary TEXT,
        started_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ,
        error_message TEXT
    );

    CREATE TABLE IF NOT EXISTS research_results (
        id UUID PRIMARY KEY,
        analysis_job_id UUID NOT NULL REFERENCES analysis_jobs(id) ON DELETE CASCADE,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        final_view TEXT NOT NULL,
        decision TEXT NOT NULL,
        confidence_score INTEGER NOT NULL,
        risk_level TEXT NOT NULL,
        market_regime TEXT NOT NULL,
        current_price NUMERIC NOT NULL,
        entry_low NUMERIC NOT NULL,
        entry_high NUMERIC NOT NULL,
        stop_loss NUMERIC NOT NULL,
        take_profit_1 NUMERIC NOT NULL,
        take_profit_2 NUMERIC NOT NULL,
        take_profit_3 NUMERIC NOT NULL,
        risk_reward_ratio NUMERIC NOT NULL,
        executive_summary TEXT NOT NULL,
        thesis TEXT NOT NULL,
        invalidation TEXT NOT NULL,
        holding_horizon TEXT NOT NULL,
        score_breakdown JSONB NOT NULL,
        detail_sections JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        id UUID PRIMARY KEY,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        action TEXT NOT NULL,
        payload JSONB,
        created_at TIMESTAMPTZ NOT NULL
    );
    """
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(schema)
            for a in ASSETS:
                cur.execute(
                    """
                    INSERT INTO assets(symbol, name, asset_class, price, change_pct)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (symbol) DO UPDATE SET
                        name = EXCLUDED.name,
                        asset_class = EXCLUDED.asset_class,
                        price = EXCLUDED.price,
                        change_pct = EXCLUDED.change_pct,
                        updated_at = now()
                    """,
                    (a["symbol"], a["name"], a["asset_class"], a["price"], a["change_pct"]),
                )


class AnalysisRequest(BaseModel):
    symbol: str = Field(..., examples=["BTCUSD"])
    asset_class: str = Field(..., examples=["Crypto"])
    timeframe: str = Field(..., examples=["1d"])
    price: float = Field(..., gt=0)
    additional_context: Optional[str] = ""


app = FastAPI(title="AI Institutional Market Research Workbench API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    for _ in range(30):
        try:
            init_db()
            redis_client().ping()
            return
        except Exception:
            time.sleep(2)
    raise RuntimeError("API failed to connect to database or Redis")


@app.get("/health")
def health():
    return {"status": "ok", "service": "api", "time": now_iso()}


@app.get("/api/assets")
def get_assets():
    rows = execute(
        "SELECT symbol, name, asset_class, price::float, change_pct::float, updated_at FROM assets ORDER BY asset_class, symbol",
        fetch=True,
    )
    return {"assets": rows, "timeframes": TIMEFRAMES}


@app.post("/api/analysis")
def create_analysis(payload: AnalysisRequest):
    job_id = str(uuid.uuid4())
    created_at = now_iso()

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO analysis_jobs
                (id, symbol, asset_class, timeframe, price, additional_context, status, current_step, progress_percent, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, 'queued', 0, 0, %s)
                """,
                (
                    job_id,
                    payload.symbol.upper(),
                    payload.asset_class,
                    payload.timeframe,
                    payload.price,
                    payload.additional_context or "",
                    created_at,
                ),
            )

            for idx, step in enumerate(PIPELINE_STEPS, start=1):
                cur.execute(
                    """
                    INSERT INTO analysis_pipeline_steps
                    (id, analysis_job_id, step_order, step_name, status)
                    VALUES (%s, %s, %s, %s, 'pending')
                    """,
                    (str(uuid.uuid4()), job_id, idx, step),
                )

            cur.execute(
                """
                INSERT INTO audit_logs(id, entity_type, entity_id, action, payload, created_at)
                VALUES (%s, 'analysis_job', %s, 'created', %s, %s)
                """,
                (str(uuid.uuid4()), job_id, json.dumps(payload.model_dump()), created_at),
            )

    redis_client().lpush(QUEUE_NAME, job_id)

    return {"job_id": job_id, "status": "queued"}


@app.get("/api/analysis/{job_id}")
def get_job(job_id: str):
    row = execute_one(
        """
        SELECT id::text, symbol, asset_class, timeframe, price::float, additional_context,
               status, current_step, progress_percent, created_at, started_at, completed_at, failed_reason
        FROM analysis_jobs WHERE id = %s
        """,
        (job_id,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    return row


@app.get("/api/analysis/{job_id}/steps")
def get_steps(job_id: str):
    rows = execute(
        """
        SELECT id::text, step_order, step_name, status, output_summary, started_at, completed_at, error_message
        FROM analysis_pipeline_steps
        WHERE analysis_job_id = %s
        ORDER BY step_order ASC
        """,
        (job_id,),
        fetch=True,
    )
    return {"steps": rows}


@app.get("/api/analysis/{job_id}/result")
def get_result(job_id: str):
    row = execute_one(
        """
        SELECT id::text, analysis_job_id::text, symbol, timeframe, final_view, decision,
               confidence_score, risk_level, market_regime, current_price::float,
               entry_low::float, entry_high::float, stop_loss::float,
               take_profit_1::float, take_profit_2::float, take_profit_3::float,
               risk_reward_ratio::float, executive_summary, thesis, invalidation,
               holding_horizon, score_breakdown, detail_sections, created_at
        FROM research_results
        WHERE analysis_job_id = %s
        """,
        (job_id,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Research result not ready")
    return row


@app.get("/api/history")
def get_history():
    rows = execute(
        """
        SELECT j.id::text AS job_id, j.symbol, j.asset_class, j.timeframe, j.status,
               j.created_at, r.final_view, r.decision, r.confidence_score, r.risk_level
        FROM analysis_jobs j
        LEFT JOIN research_results r ON r.analysis_job_id = j.id
        ORDER BY j.created_at DESC
        LIMIT 50
        """,
        fetch=True,
    )
    return {"items": rows}


@app.get("/api/intelligence")
def get_intelligence():
    return {
        "market_regime": "Selective risk-on with elevated volatility",
        "summary": "Crypto and growth assets show tactical upside potential, but volatility remains high. USD softness is supportive, while event risk remains a key constraint.",
        "top_opportunities": [
            {"symbol": "BTCUSD", "view": "Bullish tactical setup", "confidence": 78},
            {"symbol": "XAUUSD", "view": "Bullish macro hedge", "confidence": 74},
            {"symbol": "NASDAQ", "view": "Constructive but extended", "confidence": 68},
        ],
        "risk_events": [
            "Central bank communication",
            "US dollar rebound risk",
            "High crypto volatility",
            "Equity market concentration risk",
        ],
    }
