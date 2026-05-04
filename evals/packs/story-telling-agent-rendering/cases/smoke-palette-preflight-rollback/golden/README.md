# Golden (smoke-palette-preflight-rollback)

No golden artifacts are pinned for this case in iteration 2.
The test is purely contract-driven: assertions live in
`case.yaml.expected.expectations` and check fenced output
contract blocks (`palette-preflight`, `status`) for the
expected substrings (`failing_pairs`, `customer-coral`,
`#F87171`) and forbidden statuses (`pass`, `pass_unverified`).

Promotion to a frozen golden (a checked-in
`palette-preflight.json` snapshot) can happen after a
baseline run, when rubric severity is also promoted from
`info` to `warn` / `blocker`.
