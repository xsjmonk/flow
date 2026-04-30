from __future__ import annotations

import math
from dataclasses import dataclass
import numbers
from typing import Any

from flow.engine.core.formula import Formula
from flow.engine.core.result import CalculationResult
from flow.engine.core.validation import FormulaValidationError


FORMULA_01_PIPE_CROSS_SECTION_AREA = "FORMULA_01_PIPE_CROSS_SECTION_AREA"
FORMULA_01_PIPE_CROSS_SECTION_AREA_NAME = "Pipe Cross-Section Area"


@dataclass(frozen=True)
class PipeAreaInput:
    inner_diameter_m: float
    pipe_id: str | None = None
    diameter_source: str | None = None


@dataclass(frozen=True)
class PipeAreaOutput:
    area_m2: float
    inner_diameter_m: float
    pipe_id: str | None = None
    diameter_source: str | None = None
    assumptions: list[str] | tuple[str, ...] = ()


def _validate_inner_diameter_m(inner_diameter_m: Any) -> float:
    """
    Strict validation for actual inner diameter in meters.
    """

    if inner_diameter_m is None:
        raise FormulaValidationError("inner_diameter_m must be provided (not None).")

    # Reject strings and other non-real types explicitly.
    if isinstance(inner_diameter_m, bool) or not isinstance(inner_diameter_m, numbers.Real):
        raise FormulaValidationError("inner_diameter_m must be numeric (a real number).")

    value = float(inner_diameter_m)

    if not math.isfinite(value):
        raise FormulaValidationError("inner_diameter_m must be finite (not NaN/Infinity).")

    if value <= 0.0:
        raise FormulaValidationError("inner_diameter_m must be greater than 0.")

    return value


def calculate_pipe_cross_section_area(inner_diameter_m: float) -> float:
    """
    Pure function for Formula 01:
    Area = pi * inner_diameter^2 / 4
    """

    d = _validate_inner_diameter_m(inner_diameter_m)
    return math.pi * d * d / 4.0


class PipeCrossSectionAreaFormula(Formula[PipeAreaInput]):
    formula_id: str = FORMULA_01_PIPE_CROSS_SECTION_AREA
    formula_name: str = FORMULA_01_PIPE_CROSS_SECTION_AREA_NAME

    def evaluate(self, input: PipeAreaInput) -> CalculationResult:
        d = _validate_inner_diameter_m(input.inner_diameter_m)
        area = calculate_pipe_cross_section_area(d)

        assumptions = [
            "pipe is circular",
            "diameter is actual inner diameter",
            "pipe is fully open",
            "no blockage/restriction is included",
            "area is constant along this pipe section",
        ]

        output = PipeAreaOutput(
            area_m2=area,
            inner_diameter_m=d,
            pipe_id=input.pipe_id,
            diameter_source=input.diameter_source,
            assumptions=assumptions,
        )

        return CalculationResult(
            formula_id=self.formula_id,
            formula_name=self.formula_name,
            input=input,
            output=output,
            is_valid=True,
            warnings=[],
            errors=[],
        )

