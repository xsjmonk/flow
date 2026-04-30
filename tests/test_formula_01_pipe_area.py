import math

import pytest

from flow.engine.core.validation import FormulaValidationError
from flow.engine.geometry.pipe_area import (
    FORMULA_01_PIPE_CROSS_SECTION_AREA,
    FORMULA_01_PIPE_CROSS_SECTION_AREA_NAME,
    PipeAreaInput,
    PipeCrossSectionAreaFormula,
    calculate_pipe_cross_section_area,
)


@pytest.mark.parametrize(
    "inner_diameter_m, expected",
    [
        (1.0, math.pi / 4.0),
        (2.0, math.pi),
        (0.5, math.pi * 0.5 * 0.5 / 4.0),
    ],
)
def test_calculate_pipe_cross_section_area_valid(inner_diameter_m, expected):
    area = calculate_pipe_cross_section_area(inner_diameter_m)
    assert area == pytest.approx(expected, rel=1e-12, abs=0.0)


def test_pipe_cross_section_area_scales_with_diameter_squared():
    d = 0.73
    area_d = calculate_pipe_cross_section_area(d)
    area_2d = calculate_pipe_cross_section_area(2.0 * d)
    assert area_2d == pytest.approx(4.0 * area_d, rel=1e-12, abs=0.0)


def test_formula_class_returns_expected_result_for_valid_input():
    formula = PipeCrossSectionAreaFormula()
    inp = PipeAreaInput(inner_diameter_m=1.0, pipe_id="P-1", diameter_source="user_input")
    result = formula.evaluate(inp)

    assert result.is_valid is True
    assert result.errors == []
    assert result.formula_id == FORMULA_01_PIPE_CROSS_SECTION_AREA
    assert result.formula_name == FORMULA_01_PIPE_CROSS_SECTION_AREA_NAME
    assert result.output is not None

    assert result.output.inner_diameter_m == inp.inner_diameter_m
    assert result.output.pipe_id == inp.pipe_id
    assert result.output.diameter_source == inp.diameter_source
    assert "pipe is circular" in result.output.assumptions

    expected = math.pi / 4.0
    assert result.output.area_m2 == pytest.approx(expected, rel=1e-12, abs=0.0)


@pytest.mark.parametrize(
    "inner_diameter_m",
    [
        None,
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
        "1.0",
    ],
)
def test_formula_invalid_input_raises(inner_diameter_m):
    formula = PipeCrossSectionAreaFormula()
    inp = PipeAreaInput(inner_diameter_m=inner_diameter_m)  # type: ignore[arg-type]
    with pytest.raises(FormulaValidationError):
        _ = formula.evaluate(inp)

