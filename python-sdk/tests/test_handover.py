import json

from dispersl.handover import next_action_from_tool


def test_handover_top_level() -> None:
    action = next_action_from_tool(
        {
            "type": "handover_task",
            "agent_name": "risk-manager",
            "prompt": "Check risk",
        }
    )
    assert action.type == "handover"
    assert action.to_agent == "risk-manager"


def test_handover_function_and_double_serialized() -> None:
    serialized_inner = json.dumps({"to_agent": "technical-analyst", "message": "Run analysis"})
    action = next_action_from_tool(
        {
            "function": {
                "name": "handover_task",
                "arguments": json.dumps(serialized_inner),
            }
        }
    )
    assert action.type == "handover"
    assert action.to_agent == "technical-analyst"


def test_end_marker() -> None:
    action = next_action_from_tool({"type": "end_session"})
    assert action.type == "end"
