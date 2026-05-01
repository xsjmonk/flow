import math

import pytest

from flow.engine import (
    PipeAreaInput,
    PipeAreaOutput,
    calculate_pipe_area,
    calculate_pipe_area_from_diameter,
    calculate_pipe_areas,
    pipe_area_outputs_to_records,
)


class TestCalculatePipeAreaFromDiameter:
    """Tests for the convenience function calculate_pipe_area_from_diameter."""

    def test_diameter_1_returns_pi_over_4(self):
        area = calculate_pipe_area_from_diameter(1.0)
        assert area == pytest.approx(math.pi / 4.0, rel=1e-12, abs=0.0)

    def test_diameter_2_returns_pi(self):
        area = calculate_pipe_area_from_diameter(2.0)
        assert area == pytest.approx(math.pi, rel=1e-12, abs=0.0)

    def test_diameter_0_5(self):
        area = calculate_pipe_area_from_diameter(0.5)
        expected = math.pi * 0.5 * 0.5 / 4.0
        assert area == pytest.approx(expected, rel=1e-12, abs=0.0)

    def test_diameter_0_raises_error(self):
        with pytest.raises(ValueError, match="must be greater than 0"):
            calculate_pipe_area_from_diameter(0)

    def test_negative_diameter_raises_error(self):
        with pytest.raises(ValueError, match="must be greater than 0"):
            calculate_pipe_area_from_diameter(-1.0)


class TestCalculatePipeArea:
    """Tests for the main calculate_pipe_area function."""

    def test_output_has_direct_area_m2_property(self):
        input_obj = PipeAreaInput(inner_diameter_m=1.0, pipe_id="P-1", diameter_source="user")
        result = calculate_pipe_area(input_obj)
        assert result.area_m2 == pytest.approx(math.pi / 4.0, rel=1e-12)

    def test_output_has_direct_inner_diameter_m_property(self):
        input_obj = PipeAreaInput(inner_diameter_m=1.5, pipe_id="P-2", diameter_source="CAD")
        result = calculate_pipe_area(input_obj)
        assert result.inner_diameter_m == 1.5

    def test_output_preserves_pipe_id(self):
        input_obj = PipeAreaInput(inner_diameter_m=1.0, pipe_id="TEST-001")
        result = calculate_pipe_area(input_obj)
        assert result.pipe_id == "TEST-001"

    def test_output_preserves_diameter_source(self):
        input_obj = PipeAreaInput(inner_diameter_m=1.0, diameter_source="measured")
        result = calculate_pipe_area(input_obj)
        assert result.diameter_source == "measured"


class TestCalculatePipeAreas:
    """Tests for the batch helper."""

    def test_batch_returns_one_output_per_input(self):
        inputs = [
            PipeAreaInput(inner_diameter_m=0.5),
            PipeAreaInput(inner_diameter_m=1.0),
            PipeAreaInput(inner_diameter_m=2.0),
        ]
        outputs = calculate_pipe_areas(inputs)
        assert len(outputs) == 3

    def test_batch_results_match_single_calls(self):
        inputs = [
            PipeAreaInput(inner_diameter_m=1.0),
            PipeAreaInput(inner_diameter_m=2.0),
        ]
        outputs = calculate_pipe_areas(inputs)

        single_0 = calculate_pipe_area(inputs[0])
        single_1 = calculate_pipe_area(inputs[1])

        assert outputs[0].area_m2 == single_0.area_m2
        assert outputs[1].area_m2 == single_1.area_m2


class TestPipeAreaOutputsToRecords:
    """Tests for the records conversion helper."""

    def test_records_contain_required_fields(self):
        outputs = [
            PipeAreaOutput(
                area_m2=0.5,
                inner_diameter_m=1.0,
                pipe_id="P-1",
                diameter_source="user_input",
            )
        ]
        records = pipe_area_outputs_to_records(outputs)

        assert len(records) == 1
        assert "pipe_id" in records[0]
        assert "diameter_source" in records[0]
        assert "inner_diameter_m" in records[0]
        assert "area_m2" in records[0]

    def test_records_values_match_output(self):
        outputs = [
            PipeAreaOutput(
                area_m2=0.785,
                inner_diameter_m=1.0,
                pipe_id="A",
                diameter_source="B",
            )
        ]
        records = pipe_area_outputs_to_records(outputs)

        assert records[0]["pipe_id"] == "A"
        assert records[0]["diameter_source"] == "B"
        assert records[0]["inner_diameter_m"] == 1.0
        assert records[0]["area_m2"] == 0.785