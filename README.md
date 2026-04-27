# tool-permission-gate-py

Policy-check agent tool calls before execution. Pure Python, zero deps. Python port of [`@mukundakatta/tool-permission-gate`](https://www.npmjs.com/package/@mukundakatta/tool-permission-gate).

```bash
pip install tool-permission-gate-py
```

```python
from tool_permission_gate import can_call_tool, filter_tool_calls

policy = {
    "allow": ["search", "fetch", "transfer"],
    "deny": ["shell"],
    "max_amount": 100,
    "require_human_for": ["deploy"],
}

can_call_tool({"name": "search"}, policy)
# Decision(allowed=True, reasons=[], tool='search')

can_call_tool({"name": "transfer", "args": {"amount": 500}}, policy)
# Decision(allowed=False, reasons=['amount_over_limit'], tool='transfer')

filter_tool_calls([{"name": "search"}, {"name": "shell"}], policy)
# [FilteredCall(allowed=True, ...), FilteredCall(allowed=False, reasons=['tool_denied'], ...)]
```

## License

MIT
