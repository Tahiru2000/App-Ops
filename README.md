# Troubleshooting Runbook (Django + Postgres)

## Steps
1. Use `scripts/parse_nginx.py` on access logs → detect high p95/error rates.
2. Use `scripts/parse_app_logs.py` → see if DB dominates latency.
3. Use `scripts/check_postgres_slow.py` → confirm slow queries in Postgres logs.
4. Run `django_snippets/django_explain_snippet.py` inside Django shell → confirm Seq Scan.
5. Apply model index in `django_snippets/models.py`, then `makemigrations` + `migrate`.
6. Validate with `.explain()` again (expect Index Scan).
7. Short-term: caching (see `cache_snippet.py`), DB pool (`CONN_MAX_AGE=60`), request timeouts (`timeout_middleware.py`).
8. Prevent recurrence: Prometheus alerts (`monitoring/prometheus_alerts.yaml`).

## Quick Commands
```bash
python runbook/scripts/parse_nginx.py logs/access.log
python runbook/scripts/parse_app_logs.py logs/app.log
python runbook/scripts/check_postgres_slow.py logs/postgres.log 1000
```
