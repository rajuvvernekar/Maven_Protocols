# get_all_client_data — dependency rule (CORRECTED 2026-06-17)

`get_all_client_data` is **no longer a default/auto-fetch tool**, and it is **NOT** a
dependency on every tool. It should be configured as a dependency **only on the
protocols that actually invoke it** (i.e. where `invoke `get_all_client_data`` appears).

This SUPERSEDES the earlier "Tool dependency" doc-3 instruction ("add get_all_client_data
to all tools"). Treat it like any other tool: dependency exists exactly where invoked,
nowhere else. Remove it from the SOT/config for any tool whose protocol does not invoke it.
