from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CalculationResult:
    formula_id: str
    formula_name: str
    input: Any
    output: Any | None
    is_valid: bool
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "formula_id": self.formula_id,
            "formula_name": self.formula_name,
            "is_valid": self.is_valid,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "input": self.input,
            "output": self.output,
        }

