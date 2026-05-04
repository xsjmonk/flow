import math
import pytest

from flow.engine import (
    PipeAreaInput,
    calculate_pipe_area,
    FlowVelocityInput,
    FlowVelocityOutput,
    calculate_flow_velocity,
    calculate_flow_velocity_from_rate_and_area,
    calculate_flow_velocities,
    flow_velocity_outputs_to_records,
)


class TestCalculateFlowVelocityFromRateAndArea:
    """Tests for the convenience function calculate_flow_velocity_from_rate_and_area."""

    def test_basic_velocity(self):
        velocity = calculate_flow_velocity_from_rate_and_area(volumetric_flow_rate_m3_s=10.0, area_m2=2.0)
        assert velocity == pytest.approx(5.0, rel=1e-12)

    def test_small_area(self):
        velocity = calculate_flow_velocity_from_rate_and_area(volumetric_flow_rate_m3_s=1.0, area_m2=0.5)
        assert velocity == pytest.approx(2.0, rel=1e-12)

    def test_zero_flow(self):
        velocity = calculate_flow_velocity_from_rate_and_area(volumetric_flow_rate_m3_s=0.0, area_m2=2.0)
        assert velocity == pytest.approx(0.0, rel=1e-12)

    def test_negative_flow(self):
        velocity = calculate_flow_velocity_from_rate_and_area(volumetric_flow_rate_m3_s=-5.0, area_m2=1.0)
        assert velocity == pytest.approx(-5.0, rel=1e-12)

    def test_zero_area_raises_error(self):
        with pytest.raises(ValueError, match="area_m2 must be greater than 0"):
            calculate_flow_velocity_from_rate_and_area(volumetric_flow_rate_m3_s=10.0, area_m2=0)

    def test_negative_area_raises_error(self):
        with pytest.raises(ValueError, match="area_m2 must be greater than 0"):
            calculate_flow_velocity_from_rate_and_area(volumetric_flow_rate_m3_s=10.0, area_m2=-1.0)


class TestCalculateFlowVelocity:
    """Tests for the main calculate_flow_velocity function."""

    def test_output_has_direct_velocity_m_s_property(self):
        input_obj = FlowVelocityInput(volumetric_flow_rate_m3_s=10.0, area_m2=2.0)
        result = calculate_flow_velocity(input_obj)
        assert result.velocity_m_s == pytest.approx(5.0, rel=1e-12)

    def test_output_has_direct_area_m2_property(self):
        input_obj = FlowVelocityInput(volumetric_flow_rate_m3_s=10.0, area_m2=1.5)
        result = calculate_flow_velocity(input_obj)
        assert result.area_m2 == 1.5

    def test_output_has_direct_volumetric_flow_rate_property(self):
        input_obj = FlowVelocityInput(volumetric_flow_rate_m3_s=7.5, area_m2=1.0)
        result = calculate_flow_velocity(input_obj)
        assert result.volumetric_flow_rate_m3_s == 7.5

    def test_output_preserves_flow_id(self):
        input_obj = FlowVelocityInput(
            volumetric_flow_rate_m3_s=10.0, area_m2=1.0, flow_id="F-001"
        )
        result = calculate_flow_velocity(input_obj)
        assert result.flow_id == "F-001"

    def test_output_preserves_area_source(self):
        input_obj = FlowVelocityInput(
            volumetric_flow_rate_m3_s=10.0, area_m2=1.0, area_source="formula_01"
        )
        result = calculate_flow_velocity(input_obj)
        assert result.area_source == "formula_01"

    def test_zero_area_raises_error(self):
        input_obj = FlowVelocityInput(volumetric_flow_rate_m3_s=10.0, area_m2=0)
        with pytest.raises(ValueError, match="area_m2 must be greater than 0"):
            calculate_flow_velocity(input_obj)


class TestCalculateFlowVelocities:
    """Tests for the batch helper."""

    def test_batch_returns_one_output_per_input(self):
        inputs = [
            FlowVelocityInput(volumetric_flow_rate_m3_s=5.0, area_m2=1.0),
            FlowVelocityInput(volumetric_flow_rate_m3_s=10.0, area_m2=2.0),
            FlowVelocityInput(volumetric_flow_rate_m3_s=15.0, area_m2=3.0),
        ]
        outputs = calculate_flow_velocities(inputs)
        assert len(outputs) == 3

    def test_batch_results_match_single_calls(self):
        inputs = [
            FlowVelocityInput(volumetric_flow_rate_m3_s=10.0, area_m2=2.0),
            FlowVelocityInput(volumetric_flow_rate_m3_s=20.0, area_m2=2.0),
        ]
        outputs = calculate_flow_velocities(inputs)

        single_0 = calculate_flow_velocity(inputs[0])
        single_1 = calculate_flow_velocity(inputs[1])

        assert outputs[0].velocity_m_s == single_0.velocity_m_s
        assert outputs[1].velocity_m_s == single_1.velocity_m_s


class TestFlowVelocityOutputsToRecords:
    """Tests for the records conversion helper."""

    def test_records_contain_required_fields(self):
        outputs = [
            FlowVelocityOutput(
                velocity_m_s=5.0,
                volumetric_flow_rate_m3_s=10.0,
                area_m2=2.0,
                flow_id="F-1",
                area_source="test",
            )
        ]
        records = flow_velocity_outputs_to_records(outputs)

        assert len(records) == 1
        assert "flow_id" in records[0]
        assert "area_source" in records[0]
        assert "volumetric_flow_rate_m3_s" in records[0]
        assert "area_m2" in records[0]
        assert "velocity_m_s" in records[0]

    def test_records_values_match_output(self):
        outputs = [
            FlowVelocityOutput(
                velocity_m_s=5.0,
                volumetric_flow_rate_m3_s=10.0,
                area_m2=2.0,
                flow_id="A",
                area_source="B",
            )
        ]
        records = flow_velocity_outputs_to_records(outputs)

        assert records[0]["flow_id"] == "A"
        assert records[0]["area_source"] == "B"
        assert records[0]["volumetric_flow_rate_m3_s"] == 10.0
        assert records[0]["area_m2"] == 2.0
        assert records[0]["velocity_m_s"] == 5.0


class TestFormula01ToFormula02Chain:
    """Tests for chaining Formula 01 output to Formula 02 input."""

    def test_formula_01_output_chains_to_formula_02(self):
        # Calculate area using Formula 01
        area_result = calculate_pipe_area(PipeAreaInput(inner_diameter_m=0.5))
        area_value = area_result.area_m2

        # Use area directly in Formula 02
        velocity_input = FlowVelocityInput(
            volumetric_flow_rate_m3_s=0.01,
            area_m2=area_value,
            flow_id=area_result.pipe_id,
            area_source="formula_01_pipe_area",
        )
        velocity_result = calculate_flow_velocity(velocity_input)

        # Verify chain works
        expected_velocity = 0.01 / (math.pi * 0.5 * 0.5 / 4.0)
        assert velocity_result.velocity_m_s == pytest.approx(expected_velocity, rel=1e-12)
        assert velocity_result.area_m2 == area_value
