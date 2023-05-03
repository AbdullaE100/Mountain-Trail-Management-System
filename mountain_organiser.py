from __future__ import annotations
from mountain import Mountain
import bisect

class MountainOrganiser:

    def __init__(self) -> None:
        self.mountains = []

    def add_mountains(self, mountains: list[Mountain]) -> None:
        for mountain in mountains:
            bisect.insort(self.mountains, (mountain.length, mountain.name))

    def cur_position(self, mountain: Mountain) -> int:
        position = bisect.bisect_left(self.mountains, (mountain.length, mountain.name))
        if position != len(self.mountains) and self.mountains[position] == (mountain.length, mountain.name):
            return position
        else:
            raise KeyError("Mountain not found")
