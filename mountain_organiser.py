from __future__ import annotations
from mountain import Mountain
import bisect

class MountainOrganiser:

    def __init__(self) -> None:
        """
        Initializes a new MountainOrganiser instance.

        :complexity: O(1) for initializing the empty list of mountains.
        """
        self.mountains = []

    def add_mountains(self, mountains: list[Mountain]) -> None:
        """
        :complexity: O(n * log(n)) where n is the number of mountains to be added.
        This is due to the bisect.insort method which has a complexity of O(log(n)) per insertion."""
        for mountain in mountains:
            bisect.insort(self.mountains, (mountain.length, mountain.name))

    def cur_position(self, mountain: Mountain) -> int:
        """
        :complexity: O(log(n)) where n is the number of mountains in the list.
                     This is due to the bisect.bisect_left method which has a complexity of O(log(n)).
        """
        position = bisect.bisect_left(self.mountains, (mountain.length, mountain.name))
        if position != len(self.mountains) and self.mountains[position] == (mountain.length, mountain.name):
            return position
        else:
            raise KeyError("Mountain not found")
