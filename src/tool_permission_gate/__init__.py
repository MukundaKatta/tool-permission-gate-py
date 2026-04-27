"""tool_permission_gate -- policy-check agent tool calls before execution.

Public API:
    can_call_tool(call, policy=None) -> Decision
    filter_tool_calls(calls, policy) -> list[FilteredCall]
"""

from dataclasses import dataclass, field
from typing import Any, Iterable, Optional


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reasons: list[str]
    tool: Optional[str] = None


@dataclass(frozen=True)
class FilteredCall:
    call: Any
    allowed: bool
    reasons: list[str]
    tool: Optional[str]


def _tool_name(call: Any) -> Optional[str]:
    if not isinstance(call, dict):
        return None
    return call.get("name") or call.get("tool")


def can_call_tool(call: Any, policy: Optional[dict] = None) -> Decision:
    """Decide whether a single tool call is permitted under the policy.

    Policy keys (all optional):
        - allow: list of tool names to allow (any tool not in this list is denied)
        - deny: list of tool names to deny outright
        - max_amount / maxAmount: numeric ceiling on call.args.amount
        - require_human_for / requireHumanFor: list of tool names that require call.approved=True
    """
    policy = policy or {}
    name = _tool_name(call)
    allowed = policy.get("allow") or []
    denied = policy.get("deny") or []
    max_amount = policy.get("max_amount", policy.get("maxAmount"))
    require_human_for = policy.get("require_human_for") or policy.get("requireHumanFor") or []

    reasons: list[str] = []
    if allowed and name not in allowed:
        reasons.append("tool_not_allowed")
    if name in denied:
        reasons.append("tool_denied")
    if max_amount is not None and isinstance(call, dict):
        amt = (call.get("args") or {}).get("amount")
        if isinstance(amt, (int, float)) and amt > max_amount:
            reasons.append("amount_over_limit")
    if name in require_human_for and (not isinstance(call, dict) or not call.get("approved")):
        reasons.append("human_approval_required")

    return Decision(allowed=len(reasons) == 0, reasons=reasons, tool=name)


def filter_tool_calls(calls: Iterable[Any], policy: Optional[dict] = None) -> list[FilteredCall]:
    """Apply ``can_call_tool`` to each call and return per-call decisions."""
    return [
        FilteredCall(call=c, allowed=d.allowed, reasons=d.reasons, tool=d.tool)
        for c in calls
        for d in [can_call_tool(c, policy)]
    ]


__version__ = "0.1.0"
__all__ = ["can_call_tool", "filter_tool_calls", "Decision", "FilteredCall"]
