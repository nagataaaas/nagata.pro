from dataclasses import dataclass


class Connection:
    pass


@dataclass(frozen=True)
class Horizontal(Connection):
    height: int


@dataclass(frozen=True)
class Vertical(Connection):
    width: int


@dataclass(frozen=True)
class All(Connection):
    pass
