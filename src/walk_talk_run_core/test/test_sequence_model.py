from walk_talk_run_core.sequence_model import validate_sequence


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


def test_validate_sequence_accepts_motion_distance():
    sequence = [
        {"type": "motion_distance", "distance": 2.0, "speed": 0.3},
    ]

    validated = validate_sequence(sequence, max_linear_speed=1.0, max_angular_speed=1.0)

    assert len(validated) == 1
    assert validated[0]["type"] == "motion_distance"
    assert validated[0]["distance"] == 2.0
    assert validated[0]["speed"] == 0.3


def test_validate_sequence_accepts_motion_angle():
    sequence = [
        {"type": "motion_angle", "angle": 1.57, "speed": 0.5},
    ]

    validated = validate_sequence(sequence, max_linear_speed=1.0, max_angular_speed=1.0)

    assert len(validated) == 1
    assert validated[0]["type"] == "motion_angle"
    assert validated[0]["angle"] == 1.57
    assert validated[0]["speed"] == 0.5


def test_validate_sequence_rejects_motion_distance_zero_distance():
    sequence = [{"type": "motion_distance", "distance": 0.0, "speed": 0.3}]

    try:
        validate_sequence(sequence, max_linear_speed=1.0, max_angular_speed=1.0)
    except ValueError as exc:
        assert "distance must be non-zero" in str(exc)
        return

    raise AssertionError("expected rejection for zero distance")


def test_validate_sequence_rejects_motion_angle_zero_angle():
    sequence = [{"type": "motion_angle", "angle": 0.0, "speed": 0.5}]

    try:
        validate_sequence(sequence, max_linear_speed=1.0, max_angular_speed=1.0)
    except ValueError as exc:
        assert "angle must be non-zero" in str(exc)
        return

    raise AssertionError("expected rejection for zero angle")


def test_validate_sequence_rejects_motion_distance_excessive_speed():
    sequence = [{"type": "motion_distance", "distance": 2.0, "speed": 1.5}]

    try:
        validate_sequence(sequence, max_linear_speed=1.0, max_angular_speed=1.0)
    except ValueError as exc:
        assert "speed exceeds limit" in str(exc)
        return

    raise AssertionError("expected rejection for excessive speed")


def test_validate_sequence_mixed_types():
    sequence = [
        {"type": "motion_distance", "distance": 1.0, "speed": 0.3},
        {"type": "speech", "text": "到达", "pause_after_sec": 1.0},
        {"type": "motion_angle", "angle": -1.57, "speed": 0.5},
        {"type": "pause", "duration": 0.5},
    ]

    validated = validate_sequence(sequence, max_linear_speed=1.0, max_angular_speed=1.0)

    assert len(validated) == 4
    assert [s["type"] for s in validated] == [
        "motion_distance",
        "speech",
        "motion_angle",
        "pause",
    ]


def test_validate_sequence_rejects_unknown_type():
    sequence = [{"type": "fly", "altitude": 10.0}]

    try:
        validate_sequence(sequence, max_linear_speed=1.0, max_angular_speed=1.0)
    except ValueError as exc:
        assert "unsupported type" in str(exc)
        return

    raise AssertionError("expected rejection for unknown type")
