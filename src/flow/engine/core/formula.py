from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .result import CalculationResult

TInput = TypeVar("TInput")


class Formula(ABC, Generic[TInput]):
    """
    Minimal formula contract.

    Each formula:
    - has a stable `formula_id`
    - has a readable `formula_name`
    - validates and computes in `evaluate(input) -> CalculationResult`
    """

    formula_id: str
    formula_name: str

    @abstractmethod
    def evaluate(self, input: TInput) -> CalculationResult:
        raise NotImplementedError

