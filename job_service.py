"""Job and rubric validation rules independent from the UI."""

from __future__ import annotations

from typing import Any


class RubricValidationError(ValueError):
    pass


def validate_rubric(rubric: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rubric:
        raise RubricValidationError("Rubric phải có ít nhất một tiêu chí.")
    normalized: list[dict[str, Any]] = []
    total = 0
    for index, item in enumerate(rubric, start=1):
        criterion = str(item.get("criterion", "")).strip()
        if not criterion:
            raise RubricValidationError(f"Tiêu chí số {index} chưa có tên.")
        try:
            weight = int(item.get("weight", 0))
        except (TypeError, ValueError) as exc:
            raise RubricValidationError(f"Trọng số của '{criterion}' không hợp lệ.") from exc
        if weight <= 0 or weight > 100:
            raise RubricValidationError(f"Trọng số của '{criterion}' phải từ 1 đến 100.")
        total += weight
        normalized.append(
            {
                "criterion": criterion,
                "type": str(item.get("type", "Chấm điểm")).strip() or "Chấm điểm",
                "weight": weight,
                "description": str(item.get("description", "")).strip(),
            }
        )
    if total != 100:
        raise RubricValidationError(f"Tổng trọng số rubric phải bằng 100%, hiện tại là {total}%.")
    return normalized
