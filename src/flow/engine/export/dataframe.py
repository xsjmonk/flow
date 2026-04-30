from __future__ import annotations

from typing import Iterable, Any

from flow.engine.core.result import CalculationResult


def results_to_records(results: Iterable[CalculationResult]) -> list[dict[str, Any]]:
    return [r.to_dict() for r in results]


def results_to_dataframe(results: Iterable[CalculationResult]):
    """
    Optional pandas conversion helper.
    """

    import pandas as pd  # available in the Conda environment

    records = results_to_records(results)
    # Use `output` as a nested dict; flattening is left to the notebook.
    return pd.DataFrame(records)

