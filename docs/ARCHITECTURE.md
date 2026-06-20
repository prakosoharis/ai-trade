# Architecture

```text
User Browser
    ↓
Next.js Web
    ↓
FastAPI API
    ↓
PostgreSQL
Redis Queue
    ↓
Research Worker
    ↓
Research Result
```

## Local Docker Mapping

| Component | Docker Service |
|---|---|
| Frontend | web |
| API | api |
| Worker | worker |
| Database | postgres |
| Queue/Cache | redis |
| DB Viewer | adminer |

## AWS Future Mapping

| Local | AWS |
|---|---|
| web | ECS Fargate / CloudFront |
| api | ECS Fargate |
| worker | ECS Fargate worker |
| postgres | RDS PostgreSQL |
| redis | ElastiCache Redis |
| redis queue | SQS |
| local file | S3 |
| logs | CloudWatch |
