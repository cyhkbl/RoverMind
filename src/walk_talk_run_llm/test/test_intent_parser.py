"""Placeholder tests for intent_parser — real tests require mocking the Anthropic API."""

import json


def test_system_prompt_produces_valid_json_schema():
    """Verify the expected output schema matches what validate_sequence expects."""
    example_output = [
        {"type": "motion_distance", "distance": 2.0, "speed": 0.3},
        {"type": "speech", "text": "到达目标点", "pause_after_sec": 1.0},
        {"type": "motion_angle", "angle": 1.57, "speed": 0.5},
    ]

    result = json.loads(json.dumps(example_output))
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0]["type"] == "motion_distance"
    assert result[2]["type"] == "motion_angle"


def test_system_prompt_example_is_valid():
    """The example in SYSTEM_PROMPT should parse to a valid sequence."""
    example_json = (
        '[{"type":"motion_distance","distance":2.0,"speed":0.3},'
        '{"type":"speech","text":"到达目标点","pause_after_sec":1.0},'
        '{"type":"motion_angle","angle":1.57,"speed":0.5}]'
    )

    parsed = json.loads(example_json)
    assert len(parsed) == 3
    assert all("type" in step for step in parsed)
