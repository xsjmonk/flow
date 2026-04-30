class FormulaValidationError(ValueError):
    """
    Raised when a formula input fails physical/format requirements.
    """

    def __init__(self, message: str):
        super().__init__(message)

