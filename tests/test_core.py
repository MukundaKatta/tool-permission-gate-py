from tool_permission_gate import can_call_tool, filter_tool_calls


def test_no_policy_allows_everything():
    d = can_call_tool({"name": "anything"})
    assert d.allowed is True


def test_allowlist_blocks_unlisted():
    d = can_call_tool({"name": "send_email"}, {"allow": ["search"]})
    assert d.allowed is False
    assert "tool_not_allowed" in d.reasons


def test_allowlist_permits_listed():
    d = can_call_tool({"name": "search"}, {"allow": ["search"]})
    assert d.allowed is True


def test_denylist_blocks_explicitly():
    d = can_call_tool({"name": "shell"}, {"deny": ["shell"]})
    assert d.allowed is False
    assert "tool_denied" in d.reasons


def test_max_amount_enforced():
    d = can_call_tool(
        {"name": "transfer", "args": {"amount": 100}},
        {"max_amount": 50},
    )
    assert d.allowed is False
    assert "amount_over_limit" in d.reasons


def test_max_amount_under_limit_passes():
    d = can_call_tool(
        {"name": "transfer", "args": {"amount": 25}},
        {"max_amount": 50},
    )
    assert d.allowed is True


def test_human_approval_required_without_flag():
    d = can_call_tool(
        {"name": "deploy"},
        {"require_human_for": ["deploy"]},
    )
    assert d.allowed is False
    assert "human_approval_required" in d.reasons


def test_human_approval_with_flag_allows():
    d = can_call_tool(
        {"name": "deploy", "approved": True},
        {"require_human_for": ["deploy"]},
    )
    assert d.allowed is True


def test_filter_returns_per_call_decisions():
    results = filter_tool_calls(
        [{"name": "search"}, {"name": "shell"}],
        {"allow": ["search"], "deny": ["shell"]},
    )
    assert len(results) == 2
    assert results[0].allowed is True
    assert results[1].allowed is False
