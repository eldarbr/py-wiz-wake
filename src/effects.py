from typing import Protocol


class EffectCurve(Protocol):
    def get_value(self, x: float) -> float: ...


class LinearCapped(EffectCurve):
    """
    WIZ-light minimum luminance is 10%
    This linear effect maps x[0;1] to y[0.1;1]
    """

    def get_value(self, x: float) -> float:
        return 0.9 * x + 0.1
