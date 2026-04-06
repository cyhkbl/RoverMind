import json
from pathlib import Path


def default_sequence():
    return [
        {"type": "motion", "linear_x": 0.35, "linear_y": 0.0, "angular_z": 0.0, "duration": 2.0},
        {"type": "speech", "text": "Reached checkpoint one.", "pause_after_sec": 1.0},
        {"type": "motion", "linear_x": 0.0, "linear_y": 0.0, "angular_z": -0.45, "duration": 1.8},
        {"type": "motion", "linear_x": 0.35, "linear_y": 0.0, "angular_z": 0.0, "duration": 2.0},
        {"type": "speech", "text": "Reached checkpoint two.", "pause_after_sec": 1.0},
        {"type": "pause", "duration": 0.5},
    ]


def load_sequence(path):
    if not path:
        return default_sequence()

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("sequence file must contain a JSON array")
    return payload


def validate_sequence(sequence, max_linear_speed, max_angular_speed):
    if not isinstance(sequence, list) or not sequence:
        raise ValueError("sequence must be a non-empty list")

    validated = []
    for index, step in enumerate(sequence):
        if not isinstance(step, dict):
            raise ValueError(f"step {index} must be an object")

        step_type = step.get("type")
        if step_type == "motion":
            duration = float(step.get("duration", 0.0))
            linear_x = float(step.get("linear_x", 0.0))
            linear_y = float(step.get("linear_y", 0.0))
            angular_z = float(step.get("angular_z", 0.0))
            if duration <= 0.0:
                raise ValueError(f"step {index} duration must be positive")
            if abs(linear_x) > max_linear_speed or abs(linear_y) > max_linear_speed:
                raise ValueError(f"step {index} linear speed exceeds limit")
            if abs(angular_z) > max_angular_speed:
                raise ValueError(f"step {index} angular speed exceeds limit")
            validated.append(
                {
                    "type": "motion",
                    "duration": duration,
                    "linear_x": linear_x,
                    "linear_y": linear_y,
                    "angular_z": angular_z,
                }
            )
            continue

        if step_type == "speech":
            text = str(step.get("text", "")).strip()
            pause_after_sec = float(step.get("pause_after_sec", 0.0))
            if not text:
                raise ValueError(f"step {index} speech text must not be empty")
            if pause_after_sec < 0.0:
                raise ValueError(f"step {index} pause_after_sec must be non-negative")
            validated.append(
                {"type": "speech", "text": text, "pause_after_sec": pause_after_sec}
            )
            continue

        if step_type == "pause":
            duration = float(step.get("duration", 0.0))
            if duration < 0.0:
                raise ValueError(f"step {index} pause duration must be non-negative")
            validated.append({"type": "pause", "duration": duration})
            continue

        raise ValueError(f"step {index} has unsupported type: {step_type}")

    return validated
