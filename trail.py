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
        """Adds a mountain before everything currently in the trail.
    Adds a mountain before everything currently in the trail.

    :param mountain: The Mountain instance to be added before the current trail.
    :return: A new Trail instance with the added mountain before the current trail.

    :complexity: O(1) because it directly constructs a new TrailSeries and a new Trail instance.
    """
        return Trail(TrailSeries(mountain, Trail(self.store)))

    def add_empty_branch_before(self) -> Trail:
        """Adds an empty branch before everything currently in the trail.Adds an empty branch before everything currently in the trail.

    :return: A new Trail instance with the added empty branch before the current trail.

    :complexity: O(1) because it directly constructs a new TrailSplit and a new Trail instance.
    """
        return Trail(TrailSplit(Trail(None), Trail(None), Trail(self.store)))

    def follow_path(self, personality: WalkerPersonality) -> None:
        """
        Follow a path and add mountains according to a personality. 
        This implementation uses a stack to avoid recursion.
        Follow a path and add mountains according to a personality.
    This implementation uses a stack to avoid recursion.

    :param personality: The WalkerPersonality instance used to select branches during traversal.

    :complexity: O(N) where N is the number of TrailSeries (mountains) and TrailSplit (branches) in the trail.
                 Each mountain and branch is visited once.
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
            """Returns a list of all mountains on the trail.
             Returns a list of all mountains on the trail.

    :return: A list containing all Mountain instances in the trail.

    :complexity: O(N) where N is the number of TrailSeries (mountains) and TrailSplit (branches) in the trail.
                 The helper function is called once for each mountain and branch."""
            return self._collect_all_mountains_helper(self)

    def _collect_all_mountains_helper(self, current_trail) -> List[Mountain]:
        """
        A helper function for collect_all_mountains.
        Recursively collects all Mountain instances in the given trail.

        :param current_trail: The current Trail instance being processed.
        :return: A list containing all Mountain instances in the current_trail.

        :complexity: O(N) where N is the number of TrailSeries (mountains) and TrailSplit (branches) in the trail.
                    The function is called once for each mountain and branch.
        """
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
        Returns a list of all paths containing exactly k mountains.
        Paths are represented as lists of mountains.

        Paths are unique if they take a different branch, even if this results in the same set of mountains.

        :param k: The number of mountains in each path.
        :return: A list of lists containing Mountain instances, where each inner list represents a path of length k.

        :complexity: O(N * M) where N is the number of total paths and M is the maximum path length.
                    This is the complexity of calling find_all_paths() and filtering the result.
        """
        total_path = self.find_all_paths()
        length_k_path = [path for path in total_path if len(path) == k]

        return length_k_path

    def find_all_paths(self) -> list[list[Mountain]]:
        """
        Helper function for paths_of_length_k.
        Finds all paths in the trail.

        :return: A list of lists containing Mountain instances, where each inner list represents a path.

        :complexity: O(N * M) where N is the number of total paths and M is the maximum path length.
                    The function recursively traverses the trail, visiting each mountain and branch.
        """
        current_trail = self

        if current_trail == Trail(None):
            return [[]]
        elif isinstance(current_trail.store, TrailSplit):
            top_trail = current_trail.store.path_top
            bottom_trail = current_trail.store.path_bottom
            follow_trail = current_trail.store.path_follow

            all_paths_top = top_trail.find_all_paths()  # [[Mountain]]
            all_paths_bottom = bottom_trail.find_all_paths()
            all_paths_follow = follow_trail.find_all_paths()
            
            combined_paths = self.join_or_extend_paths(all_paths_top, all_paths_bottom, True)
            combined_paths = self.join_or_extend_paths(combined_paths, all_paths_follow, False)

            return combined_paths
        elif isinstance(current_trail.store, TrailSeries):
            first_mountain = current_trail.store.mountain
            follow_trail = current_trail.store.following

            stack = LinkedStack()
            combined_paths = [[first_mountain]]
            stack.push(follow_trail)

            while not stack.is_empty():
                current_trail = stack.pop()
                combined_paths = self.join_or_extend_paths(combined_paths, current_trail.find_all_paths(), False)
            return combined_paths
        


    def join_or_extend_paths(self, first_set: list[list[Mountain]], second_set: list[list[Mountain]], join) -> list[list[Mountain]]:
            """
            Joins or extends the path lists based on the 'join' parameter.

            :param first_set: A list of lists containing Mountain instances, where each inner list represents a path.
            :param second_set: A list of lists containing Mountain instances, where each inner list represents a path.
            :param join: A boolean value that indicates whether to join the two path lists (True) or extend them (False).
            :return: A list of lists containing Mountain instances, where each inner list represents a path.

            :complexity: O(N * M) where N is the number of paths in the first_set and M is the number of paths in the second_set.
                        The function iterates through each combination of paths from the two sets.
            """
            if join:
                first_set.extend(second_set)
                return first_set
            else:
                return [first + second for first in first_set for second in second_set]