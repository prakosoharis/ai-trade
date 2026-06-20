# AI Institutional Market Research Workbench — Pre-MVP

This is a Docker-ready Pre-MVP prototype for the locked MVP direction:

**Analysis Workbench → Research Pipeline → Research Result → Score Breakdown → History**

It is designed to run locally on a laptop and later on a single standard instance.

---

## 1. Requirements

Install:

- Docker Desktop
- Docker Compose v2

Check:

```bash
docker --version
docker compose version
```

---

## 2. Run Locally

```bash
cd ai-research-workbench-pre-mvp
cp .env.example .env
docker compose up -d --build
```

Open:

```text
Web App:      http://localhost:3000
API:          http://localhost:8000
API Docs:     http://localhost:8000/docs
Adminer:      http://localhost:8080
```

Adminer login:

```text
System:   PostgreSQL
Server:   postgres
Username: airesearch
Password: airesearch
Database: airesearch
```

---

## 3. Main User Flow

1. Open `http://localhost:3000`
2. Select asset class, asset, and timeframe
3. Add optional market context
4. Click **Run Institutional Analysis**
5. Watch research pipeline progress
6. Review final research result
7. Open History to see previous analysis

---

## 4. Services

| Service | Purpose |
|---|---|
| web | Next.js frontend |
| api | FastAPI backend |
| worker | Research pipeline worker |
| postgres | Main database |
| redis | Job queue and progress cache |
| adminer | Database viewer |

---

## 5. Useful Commands

Check containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

View API logs:

```bash
docker compose logs -f api
```

View worker logs:

```bash
docker compose logs -f worker
```

Stop:

```bash
docker compose down
```

Reset all data:

```bash
docker compose down -v
docker compose up -d --build
```

---

## 6. Single Instance Deployment

On your server:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git unzip
sudo systemctl enable --now docker
```

Copy the project to the server:

```bash
scp -r ai-research-workbench-pre-mvp user@SERVER_IP:/home/user/
```

Then on the server:

```bash
cd /home/user/ai-research-workbench-pre-mvp
cp .env.example .env
```

Edit `.env`:

```bash
nano .env
```

Set:

```text
NEXT_PUBLIC_API_BASE_URL=http://SERVER_IP:8000
```

Run:

```bash
docker compose up -d --build
```

Open:

```text
http://SERVER_IP:3000
http://SERVER_IP:8000/docs
```

Optional reverse proxy via Caddy:

```bash
docker compose -f docker-compose.yml -f docker-compose.instance.yml up -d --build
```

Then open:

```text
http://SERVER_IP
```

---

## 7. Backup Database

Run:

```bash
chmod +x scripts/backup_db.sh
./scripts/backup_db.sh
```

Backup files will be created in `./backups`.

---

## 8. Current Limitations

This is a Pre-MVP prototype.

Current version uses mock/hybrid research data and deterministic scoring logic. It does not yet include:

- real paid market data provider integration
- live institutional data feed
- LLM-generated research note
- machine learning
- advanced backtesting
- portfolio optimization
- production-grade compliance workflow

These are planned for post-MVP phases.
