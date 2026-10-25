"""Assignment 2: Maze Trees — MazeNode base class

=== UTM CSC148 Summer 2026 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto
Mississauga. Copying for purposes other than this use is expressly
prohibited. All forms of distribution of this code, whether as given
or with any changes, are expressly prohibited.

=== Module Description ===
A maze is a puzzle composed of cells and walls, with a designated start
cell and finish cell. The goal is to find a path from the start to the
finish by moving between adjacent cells without passing through walls.
A cell is considered adjacent to another cell if it is directly left,
right, above, or below it (or, in three dimensions, one step along the
z-axis).

Every maze in this assignment is guaranteed to be a perfect maze
with exactly one start cell and exactly one finish cell: there is
exactly one path between every two cells in the tree, including
from start to finish. Perfect mazes have no loops or cycles, so
they can be represented as trees where each cell is a node and
edges connect every pair of adjacent cells that are not separated
by a wall. You may assume this when implementing the methods in
this module.

This module defines the base class <MazeNode>, which represents a
single cell of such a tree rooted at the start cell.
"""
from __future__ import annotations

from collections import deque
from typing import Optional


def parse_cell(s: str) -> tuple[str, str]:
    """Return a tuple (<wall_string>, <kind>) for the raw cell string <s>.

    A raw cell string has the form WALLS[SF], where WALLS is a string
    of 0/1 characters describing the walls of the cell and the optional
    'S'/'F' suffix marks the cell as the start or finish of the maze.
    <kind> is one of 'start', 'finish', or 'regular'.
    """
    if s.endswith("S"):
        return s[:-1], "start"
    elif s.endswith("F"):
        return s[:-1], "finish"
    return s, "regular"


class MazeNode:
    """A single cell of a maze stored as a node in a tree.

    === Public Attributes ===
    x:
        The x coordinate of this cell.
    y:
        The y coordinate of this cell.
    kind:
        One of 'start', 'finish', or 'regular'.
    subtrees:
        Every maze cell reachable from this cell in exactly one step
        along the tree, toward the leaves.
    parent:
        The maze cell reachable from this cell in exactly one step
        along the tree, toward the root; or None when this cell is
        the root of the tree.

    === Representation Invariants ===
    - kind is exactly one of 'start', 'finish', or 'regular'.
    - If <parent> is None, then it is the root of the tree.
    - There is exactly one node in the whole tree with kind == 'start'
      and exactly one node with kind == 'finish'.
    """

    x: int
    y: int
    kind: str
    subtrees: list[MazeNode]
    parent: Optional[MazeNode]

    def __init__(self, x: int, y: int, kind: str = "regular",
                 subtrees: Optional[list[MazeNode]] = None,
                 parent: Optional[MazeNode] = None) -> None:
        """Initialize this cell at grid coordinates (<x>, <y>) with the
        given <kind> and optional <subtrees>.

        If <subtrees> is provided, set this node as the parent of each
        child in it.
        """
        self.x = x
        self.y = y
        self.kind = kind
        self.subtrees = list(subtrees) if subtrees is not None else []
        self.parent = parent

        for subtree in self.subtrees:
            subtree.parent = self

    def get_root(self) -> MazeNode:
        """Return the root of the tree that contains this cell."""
        curr = self
        while curr.parent is not None:
            curr = curr.parent
        return curr

    def make_start(self) -> None:
        """Make this cell the start cell of the maze.

        The previous start cell becomes a regular cell, and the edges
        along the path from this cell to the old start cell are reversed
        so that this cell becomes the root of the tree.

        If this cell is already the start cell, do nothing.
        """
        if self.kind == 'start':
            return

        root = self.get_root()
        if root.kind == 'start':
            root.kind = 'regular'

        self.kind = 'start'

        curr = self
        prev = None
        while curr is not None:
            next_node = curr.parent
            if next_node is not None:
                next_node.subtrees.remove(curr)
                curr.subtrees.append(next_node)
            curr.parent = prev
            prev = curr
            curr = next_node

    def make_finish(self) -> None:
        """Make this cell the finish cell of the maze.

        The previous finish cell becomes a regular cell.

        If this cell is already the finish cell, do nothing.
        """
        if self.kind == 'finish':
            return

        root = self.get_root()
        queue = deque([root])
        while queue:
            curr = queue.popleft()
            if curr.kind == 'finish':
                curr.kind = 'regular'
                break
            queue.extend(curr.subtrees)

        self.kind = 'finish'

    def preorder_solve(self) -> list[MazeNode]:
        """Return the path from the start cell to the finish cell,
        found by a preorder traversal of the tree.

        This method may be called on any node in the tree, but you
        must always search from the start cell (the root of the tree).
        """
        root = self.get_root()
        path = []

        def dfs(node: MazeNode) -> bool:
            path.append(node)
            if node.kind == 'finish':
                return True
            for child in node.subtrees:
                if dfs(child):
                    return True
            path.pop()
            return False

        dfs(root)
        return path

    def levelorder_solve(self) -> list[MazeNode]:
        """Return the path from the start cell to the finish cell,
        found by a level-order traversal of the tree.

        This method may be called on any node in the tree, but you
        must always search from the start cell (the root of the tree).
        """
        root = self.get_root()
        queue = deque([root])
        parent_map = {root: None}
        finish_node = None

        while queue:
            curr = queue.popleft()

            if curr.kind == 'finish':
                finish_node = curr
                break

            for child in curr.subtrees:
                if child not in parent_map:
                    parent_map[child] = curr
                    queue.append(child)

        if finish_node is None:
            return []

        path = []
        curr = finish_node
        while curr is not None:
            path.append(curr)
            curr = parent_map[curr]

        path.reverse()
        return path


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        "allowed-import-modules": [
            "python_ta", "typing", "collections", "__future__",
        ],
    })
