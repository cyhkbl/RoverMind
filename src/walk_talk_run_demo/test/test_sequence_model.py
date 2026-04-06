from walk_talk_run_demo.sequence_model import validate_sequence


def test_validate_sequence_accepts_basic_flow():
    sequence = [
        {"type": "motion", "linear_x": 0.2, "linear_y": 0.0, "angular_z": 0.0, "duration": 1.0},
        {"type": "speech", "text": "hello", "pause_after_sec": 0.5},
        {"type": "pause", "duration": 0.1},
    ]

    validated = validate_sequence(sequence, max_linear_speed=1.0, max_angular_speed=1.0)

    assert len(validated) == 3
    assert validated[0]["type"] == "motion"
    assert validated[1]["type"] == "speech"
    assert validated[2]["type"] == "pause"


def test_validate_sequence_rejects_excessive_speed():
    sequence = [{"type": "motion", "linear_x": 2.0, "linear_y": 0.0, "angular_z": 0.0, "duration": 1.0}]

    try:
        validate_sequence(sequence, max_linear_speed=1.0, max_angular_speed=1.0)
    except ValueError as exc:
        assert "linear speed exceeds limit" in str(exc)
        return

    raise AssertionError("expected validate_sequence to reject excessive speed")
