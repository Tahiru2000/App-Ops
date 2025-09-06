# Demo Guide — Django Troubleshooting Runbook

This guide walks through the included **demo dataset** so you (or reviewers) can run the scripts and see how the runbook works.

---

## 1. Parse Nginx Logs
Run:
```bash
python runbook/scripts/parse_nginx.py runbook/demo/access.log
```

Expected output file: `metrics_per_minute.csv`  
- Shows RPS (requests per second), p50, p95, and error rate per minute.
- In the demo, between **10:20–10:22** you’ll see p95 > 2s and error rate > 0 (504 errors).

---

## 2. Parse Application Logs
Run:
```bash
python runbook/scripts/parse_app_logs.py runbook/demo/app.log
```

Expected output file: `app_metrics_per_minute.csv`  
- Confirms that `db_time_ms` dominates total `duration_ms`.
- Example: at **10:20**, db_time ~1927 ms of total 2307 ms.

---

## 3. Parse Postgres Slow Logs
Run:
```bash
python runbook/scripts/check_postgres_slow.py runbook/demo/postgres.log 1000
```

Expected output file: `postgres_slow.csv`  
- Shows repeated slow queries:
  ```sql
  SELECT id, user_id, created_at, total
  FROM orders
  WHERE user_id = 42
  ORDER BY created_at DESC
  LIMIT 50;
  ```

---

## 4. Explain Query Plan in Django
Before applying the fix:
```text
Seq Scan on orders (cost=0.00..12345.67 rows=50 width=32)
  Filter: (user_id = 42)
```
(from `demo/explain_before.txt`) → means **full table scan**.

After adding the composite index `(user_id, created_at)`:
```text
Index Scan using idx_orders_user_created_at on orders (cost=0.43..123.45 rows=50 width=32)
  Index Cond: (user_id = 42)
```
(from `demo/explain_after.txt`) → query now uses **Index Scan**.

---

## 5. Apply the Fix
1. Add index to model (`models.py`):
   ```python
   class Meta:
       indexes = [models.Index(fields=['user', '-created_at'])]
   ```
2. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

---

## 6. Short-term Mitigations
- Use cache: `django_snippets/cache_snippet.py` (caches orders for 90s).  
- Tune DB connections: set `CONN_MAX_AGE=60` in `settings.py`.  
- Add middleware timeout: `middleware/timeout_middleware.py`.  

---

## 7. Alerts
Prometheus alert examples are in `monitoring/prometheus_alerts.yaml`:  
- Trigger if p95 > 1s for 5 minutes.  
- Trigger if error rate > 2% for 3 minutes.

---

✅ With the demo dataset, you can show the full workflow: logs → metrics → diagnosis → Django fix → validation.
