from __future__ import annotations
from dataclasses import dataclass
from mountain import Mountain

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
        """
        Returns a list of all mountains on the trail.
        This implementation uses a stack to avoid recursion.
        """
        mountains = []  # Initialize an empty list to store the mountains
        stack = [self.store]  # Initialize the stack with the root store
        while stack:  # Continue until the stack is empty
            current = stack.pop()  # Pop the top item from the stack
            if isinstance(current, TrailSeries):  # If the current store is a TrailSeries (a mountain)
                mountains.append(current.mountain)  # Add the mountain to the list of mountains
                stack.append(current.following.store)  # Push the following store to the stack
            elif isinstance(current, TrailSplit):  # If the current store is a TrailSplit (a branch)
                # Push all branch stores to the stack
                stack.extend([current.path_top.store, current.path_bottom.store, current.path_follow.store])
        return mountains

    def length_k_paths(self, k) -> List[List[Mountain]]:
        """
        Returns a list of all paths of containing exactly k mountains.
        Paths are represented as lists of mountains.

        Paths are unique if they take a different branch, even if this results in the same set of mountains.
        This implementation uses a depth-first search.
        """
        all_paths = []  # Initialize an empty list to store the paths

        def dfs(path: List[Mountain], node: TrailStore, remaining: int):
            if remaining == 0:  # If the path has exactly k mountains
                all_paths.append(path)  # Add the path to the list of paths
                return
            if isinstance(node, TrailSeries):  # If the current store is a TrailSeries (a mountain)
                dfs(path + [node.mountain], node.following.store, remaining - 1)  # Recursively call dfs with the following store and decremented remaining count
            elif isinstance(node, TrailSplit):  # If the current store is a TrailSplit (a branch)
                # Recursively call dfs for all branch stores
                dfs(path, node.path_top.store, remaining)
                dfs(path, node.path_bottom.store, remaining)
                dfs(path, node.path_follow.store, remaining)

        dfs([], self.store, k)  # Start the depth-first search with an empty path, the root store, and k as the remaining count
        return all_paths  # Return the list of paths containing exactly k mountains