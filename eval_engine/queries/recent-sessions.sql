-- All sessions in this repo over the last 30 days. Useful when you need to
-- locate a session id you forgot to record.
SELECT id, summary, created_at, updated_at
FROM sessions
WHERE repository = :repository
  AND created_at >= now() - INTERVAL '30 days'
ORDER BY created_at DESC;
