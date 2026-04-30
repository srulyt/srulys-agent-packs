-- All events for a session, ordered. The runner uses this to reconstruct
-- the invocation timeline + tool-call detail.
SELECT turn_index, timestamp, type,
       user_content, assistant_content,
       tool_start_name, tool_complete_call_id, tool_complete_success,
       tool_complete_result_content,
       usage_model, usage_input_tokens, usage_output_tokens
FROM events
WHERE session_id = :session_id
ORDER BY turn_index ASC, timestamp ASC;
