-- Session header for a captured run.
SELECT id, repository, branch, summary, created_at, updated_at
FROM sessions
WHERE id = :session_id;
