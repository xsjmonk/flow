"""
Formula 02: Flow Velocity

Equation:
    velocity_m_s = volumetric_flow_rate_m3_s / area_m2

Input:
    volumetric_flow_rate_m3_s: float (cubic meters per second)
    area_m2: float (square meters)
    flow_id: optional identifier
    area_source: optional source description

Output:
    velocity_m_s: float (meters per second)
"""

from __future__ import annotations

from dataclasses import dataclass

FLOW_VELOCITY_FORMULA_ID = "FORMULA_02_FLOW_VELOCITY"
FLOW_VELOCITY_FORMULA_NAME = "Flow Velocity"
FLOW_VELOCITY_FORMULA_EQUATION = "velocity_m_s = volumetric_flow_rate_m3_s / area_m2"


@dataclass(frozen=True)
class FlowVelocityInput:
    """
    Input for flow velocity calculation.
    
    Fields:
        volumetric_flow_rate_m3_s: Flow rate in m³/s (can be negative for reverse flow).
        area_m2: Cross-sectional area in m² (typically from Formula 01 output).
        flow_id: Optional identifier for the flow/pipe/branch.
        area_source: Optional description of where the area came from.
    """
    volumetric_flow_rate_m3_s: float
    area_m2: float
    flow_id: str | None = None
    area_source: str | None = None


@dataclass(frozen=True)
class FlowVelocityOutput:
    """
    Output from flow velocity calculation.
    
    Fields:
        velocity_m_s: Flow velocity in m/s.
        volumetric_flow_rate_m3_s: Flow rate used in calculation.
        area_m2: Area used in calculation.
        flow_id: Copy of input flow_id.
        area_source: Copy of input area_source.
    """
    velocity_m_s: float
    volumetric_flow_rate_m3_s: float
    area_m2: float
    flow_id: str | None = None
    area_source: str | None = None


def calculate_flow_velocity(input: FlowVelocityInput) -> FlowVelocityOutput:
    """
    Calculate flow velocity from input.
    
    The formula is directly visible here:
        velocity_m_s = volumetric_flow_rate_m3_s / area_m2
    
    Args:
        input: FlowVelocityInput with flow rate and area.
    
    Returns:
        FlowVelocityOutput with velocity in m/s.
    
    Raises:
        ValueError: If area_m2 <= 0
    """
    area = input.area_m2
    
    if area <= 0:
        raise ValueError("area_m2 must be greater than 0")
    
    velocity_m_s = input.volumetric_flow_rate_m3_s / area
    
    return FlowVelocityOutput(
        velocity_m_s=velocity_m_s,
        volumetric_flow_rate_m3_s=input.volumetric_flow_rate_m3_s,
        area_m2=area,
        flow_id=input.flow_id,
        area_source=input.area_source,
    )


def calculate_flow_velocity_from_rate_and_area(
    volumetric_flow_rate_m3_s: float,
    area_m2: float,
) -> float:
    """
    Convenience function to calculate velocity from rate and area.
    
    The formula is directly visible here:
        velocity_m_s = volumetric_flow_rate_m3_s / area_m2
    
    Args:
        volumetric_flow_rate_m3_s: Flow rate in m³/s.
        area_m2: Cross-sectional area in m².
    
    Returns:
        Flow velocity in m/s.
    
    Raises:
        ValueError: If area_m2 <= 0
    """
    if area_m2 <= 0:
        raise ValueError("area_m2 must be greater than 0")
    
    return volumetric_flow_rate_m3_s / area_m2


def calculate_flow_velocities(inputs: list[FlowVelocityInput]) -> list[FlowVelocityOutput]:
    """
    Batch helper for calculating velocities from multiple inputs.
    
    Useful for generating data for plotting.
    
    Args:
        inputs: List of FlowVelocityInput objects.
    
    Returns:
        List of FlowVelocityOutput objects, one per input.
    """
    return [calculate_flow_velocity(inp) for inp in inputs]


def flow_velocity_outputs_to_records(outputs: list[FlowVelocityOutput]) -> list[dict]:
    """
    Convert flow velocity outputs to flat records for easy DataFrame creation.
    
    Args:
        outputs: List of FlowVelocityOutput objects.
    
    Returns:
        List of dictionaries suitable for pd.DataFrame(records).
        Each record contains: flow_id, area_source, volumetric_flow_rate_m3_s, area_m2, velocity_m_s
    """
    records = []
    for out in outputs:
        records.append({
            "flow_id": out.flow_id,
            "area_source": out.area_source,
            "volumetric_flow_rate_m3_s": out.volumetric_flow_rate_m3_s,
            "area_m2": out.area_m2,
            "velocity_m_s": out.velocity_m_s,
        })
    return records