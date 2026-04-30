-- Files the harness can correlate to actual SUT writes/edits in this session.
SELECT file_path, tool_name, turn_index, first_seen_at
FROM session_files
WHERE session_id = :session_id
ORDER BY first_seen_at ASC;
