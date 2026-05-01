"""
Formula 01: Pipe Cross-Section Area

Equation:
    Area = pi * inner_diameter_m^2 / 4

Input:
    inner_diameter_m: float (meters) - actual inner diameter, not nominal

Output:
    area_m2: float (square meters) - pipe internal cross-sectional area
"""

from __future__ import annotations

import math
from dataclasses import dataclass


FORMULA_ID = "FORMULA_01"
FORMULA_NAME = "Pipe Cross-Section Area"
FORMULA_EQUATION = "Area = pi * inner_diameter_m^2 / 4"


@dataclass(frozen=True)
class PipeAreaInput:
    """
    Input for pipe area calculation.
    
    Fields:
        inner_diameter_m: Actual pipe inner diameter in meters (not nominal, not outer).
        pipe_id: Optional identifier for the pipe.
        diameter_source: Optional description of where the diameter came from.
    """
    inner_diameter_m: float
    pipe_id: str | None = None
    diameter_source: str | None = None


@dataclass(frozen=True)
class PipeAreaOutput:
    """
    Output from pipe area calculation.
    
    Fields:
        area_m2: Cross-sectional area in square meters.
        inner_diameter_m: The diameter used in the calculation.
        pipe_id: Copy of input pipe_id.
        diameter_source: Copy of input diameter_source.
    """
    area_m2: float
    inner_diameter_m: float
    pipe_id: str | None = None
    diameter_source: str | None = None


def calculate_pipe_area(input: PipeAreaInput) -> PipeAreaOutput:
    """
    Calculate pipe cross-sectional area from input.
    
    The formula is directly visible here:
        Area = pi * inner_diameter_m^2 / 4
    
    Args:
        input: PipeAreaInput with inner_diameter_m in meters.
    
    Returns:
        PipeAreaOutput with area in square meters.
    
    Raises:
        ValueError: If inner_diameter_m <= 0
    """
    d = input.inner_diameter_m
    
    if d <= 0:
        raise ValueError("inner_diameter_m must be greater than 0")
    
    area_m2 = math.pi * d * d / 4.0
    
    return PipeAreaOutput(
        area_m2=area_m2,
        inner_diameter_m=d,
        pipe_id=input.pipe_id,
        diameter_source=input.diameter_source,
    )


def calculate_pipe_area_from_diameter(inner_diameter_m: float) -> float:
    """
    Convenience function to calculate pipe area from just a diameter value.
    
    The formula is directly visible here:
        Area = pi * inner_diameter_m^2 / 4
    
    Args:
        inner_diameter_m: Pipe inner diameter in meters.
    
    Returns:
        Cross-sectional area in square meters.
    
    Raises:
        ValueError: If inner_diameter_m <= 0
    """
    if inner_diameter_m <= 0:
        raise ValueError("inner_diameter_m must be greater than 0")
    
    return math.pi * inner_diameter_m * inner_diameter_m / 4.0


def calculate_pipe_areas(inputs: list[PipeAreaInput]) -> list[PipeAreaOutput]:
    """
    Batch helper for calculating pipe areas from multiple inputs.
    
    Useful for generating data for plotting.
    
    Args:
        inputs: List of PipeAreaInput objects.
    
    Returns:
        List of PipeAreaOutput objects, one per input.
    """
    return [calculate_pipe_area(inp) for inp in inputs]


def pipe_area_outputs_to_records(outputs: list[PipeAreaOutput]) -> list[dict]:
    """
    Convert pipe area outputs to flat records for easy DataFrame creation.
    
    Args:
        outputs: List of PipeAreaOutput objects.
    
    Returns:
        List of dictionaries suitable for pd.DataFrame(records).
        Each record contains: pipe_id, diameter_source, inner_diameter_m, area_m2
    """
    records = []
    for out in outputs:
        records.append({
            "pipe_id": out.pipe_id,
            "diameter_source": out.diameter_source,
            "inner_diameter_m": out.inner_diameter_m,
            "area_m2": out.area_m2,
        })
    return records