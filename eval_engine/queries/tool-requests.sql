-- Tool-call arguments for a session. Used to derive file_accesses[] and
-- to attribute calls to a sub-agent invocation when the parent is a `task`.
SELECT tool_call_id, name, arguments_json
FROM tool_requests
WHERE session_id = :session_id;
