from typing import Protocol


class EffectCurve(Protocol):
    def get_value(self, x: float) -> float:
        ...


class Linear(EffectCurve):
    def get_value(self, x: float) -> float:
        return x
