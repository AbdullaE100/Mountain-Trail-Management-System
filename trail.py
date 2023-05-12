from __future__ import annotations
from dataclasses import dataclass
from mountain import Mountain
from data_structures.linked_stack import LinkedStack

from typing import TYPE_CHECKING, List, Union

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from personality import WalkerPersonality

@dataclass
class TrailSplit:
    """
    A split in the trail.
       ___path_top____
      /               \
    -<                 >-path_follow-
      \__path_bottom__/
    """

    path_top: Trail
    path_bottom: Trail
    path_follow: Trail

    def remove_branch(self) -> TrailStore:
        """Removes the branch, should just leave the remaining following trail."""
        return self.path_follow.store

@dataclass
class TrailSeries:
    """
    A mountain, followed by the rest of the trail

    --mountain--following--

    """

    mountain: Mountain
    following: Trail

    def remove_mountain(self) -> TrailStore:
        """Removes the mountain at the beginning of this series."""
        return self.following.store

    def add_mountain_before(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain in series before the current one."""
        return TrailSeries(mountain, Trail(self))

    def add_empty_branch_before(self) -> TrailStore:
        """Adds an empty branch, where the current trailstore is now the following path."""
        return TrailSplit(Trail(None), Trail(None), Trail(self))

    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain after the current mountain, but before the following trail."""
        return TrailSeries(self.mountain, Trail(TrailSeries(mountain, self.following)))

    def add_empty_branch_after(self) -> TrailStore:
        """Adds an empty branch after the current mountain, but before the following trail."""
        return TrailSeries(self.mountain, Trail(TrailSplit(Trail(None), Trail(None), self.following)))

TrailStore = Union[TrailSplit, TrailSeries, None]

@dataclass
class Trail:

    store: TrailStore = None

    def add_mountain_before(self, mountain: Mountain) -> Trail:
        """Adds a mountain before everything currently in the trail."""
        return Trail(TrailSeries(mountain, Trail(self.store)))

    def add_empty_branch_before(self) -> Trail:
        """Adds an empty branch before everything currently in the trail."""
        return Trail(TrailSplit(Trail(None), Trail(None), Trail(self.store)))

    def follow_path(self, personality: WalkerPersonality) -> None:
        """
        Follow a path and add mountains according to a personality. 
        This implementation uses a stack to avoid recursion.
        """
        stack = [(self.store, False)]  # Initialize stack with the root store and a flag indicating if the branch has been visited
        while stack:  # Continue until the stack is empty
            current, branch_visited = stack.pop()  # Pop the top item from the stack
            if isinstance(current, TrailSeries):  # If the current store is a TrailSeries (a mountain)
                personality.add_mountain(current.mountain)  # Add the mountain to the personality's list of mountains
                stack.append((current.following.store, False))  # Push the following store to the stack
            elif isinstance(current, TrailSplit):  # If the current store is a TrailSplit (a branch)
                if not branch_visited:  # If the branch has not been visited yet
                    stack.append((current, True))  # Mark the branch as visited and push it back onto the stack
                    branch = current.path_top if personality.select_branch(current.path_top, current.path_bottom) else current.path_bottom
                    stack.append((branch.store, False))  # Push the selected branch's store to the stack
                else:  # If the branch has already been visited
                    stack.append((current.path_follow.store, False))  # Push the following store to the stack

    def collect_all_mountains(self) -> List[Mountain]:
            """Returns a list of all mountains on the trail."""
            return self._collect_all_mountains_helper(self)

    def _collect_all_mountains_helper(self, current_trail) -> List[Mountain]:
        empty = Trail(None)
        mountain_list = []

        if isinstance(current_trail.store, TrailSplit):
            path_top = current_trail.store.path_top
            path_bottom = current_trail.store.path_bottom
            following_path = current_trail.store.path_follow

            if following_path != empty:
                mountain_list.extend(self._collect_all_mountains_helper(following_path))
            if path_bottom != empty:
                mountain_list.extend(self._collect_all_mountains_helper(path_bottom))
            if path_top != empty:
                mountain_list.extend(self._collect_all_mountains_helper(path_top))

        elif isinstance(current_trail.store, TrailSeries):
            mountain = current_trail.store.mountain
            following_path = current_trail.store.following

            if following_path != empty:
                mountain_list.extend(self._collect_all_mountains_helper(following_path))
            mountain_list.append(mountain)

        return mountain_list
        

    def length_k_paths(self, k) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        """
        Returns a list of all paths of containing exactly k mountains.
        Paths are represented as lists of mountains.

        Paths are unique if they take a different branch, even if this results in the same set of mountains.
        """
        total_path = self.search_all_path()
        length_k_path = [path for path in total_path if len(path) == k]

        return length_k_path

    def search_all_path(self) -> list[list[Mountain]]:
        """
        Helper function for length_k_paths.
        """
        current_trail = self

        if current_trail == Trail(None):
            return [[]]
        elif isinstance(current_trail.store, TrailSplit):
            trail_top = current_trail.store.path_top
            trail_bottom = current_trail.store.path_bottom
            trail_follow = current_trail.store.path_follow

            all_path_top = trail_top.search_all_path()  # [[Mountain]]
            all_path_bottom = trail_bottom.search_all_path()
            all_path_follow = trail_follow.search_all_path()
            
            total_path = self.extend_list(all_path_top, all_path_bottom,True)
            total_path = self.extend_list(total_path, all_path_follow,False)

            return total_path
        elif isinstance(current_trail.store, TrailSeries):
            initial_mountain = current_trail.store.mountain
            trail_follow = current_trail.store.following

            call_stack = LinkedStack()
            total_path = [[initial_mountain]]
            call_stack.push(trail_follow)

            while not call_stack.is_empty():
                current_trail = call_stack.pop()
                total_path = self.extend_list(total_path, current_trail.search_all_path(),False)
            return total_path
        


    def extend_list(self, first_part: list[list[Mountain]], second_part: list[list[Mountain]], is_join) -> list[list[Mountain]]:
        """
        Return all combination of paths from first part and second part
        Example: 
        first_part = [[a],[b]]
        second_part = [[c,d],[e]]
        if is_join is True, just extends
            return [[a],[b],[c,d],[e]]
        else
            return [[a,c,d],[a,e],[b,c,d],[b,e]]
        """
        if is_join:
            first_part.extend(second_part)
            return first_part
        else:
            return [first + second for first in first_part for second in second_part] # all combination