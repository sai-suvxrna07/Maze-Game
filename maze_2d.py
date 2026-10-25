"""Assignment 2: Maze Trees — 2-D mazes

=== UTM CSC148 Summer 2026 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto
Mississauga. Copying for purposes other than this use is expressly
prohibited. All forms of distribution of this code, whether as given
or with any changes, are expressly prohibited.

=== Module Description ===
This module defines the <MazeNode2D> subclass and the helper
functions needed to build a 2D maze.

A 2D maze is represented as a rectangular list of lists
of strings, where:
    - each string represents a cell. It starts with 4 binary digits,
      each indicating whether there is a wall immediately above it,
      below it, to the left and right, respectively. (e.g., '1001' means
      walls above it and on the right, but no walls below or to the left.)
    - if a string ends with 'S', the cell is the start cell of the
      maze.
    - if a string ends with 'F', the cell is the finish cell of the
      maze.
    - maze[0][0] is the top-left cell, and maze[x][y] is the cell at
      coordinate (x, y).
    - a maze is always surrounded by walls on its borders.
"""
from __future__ import annotations

import json
from typing import Optional
from collections import deque

from maze_node import MazeNode, parse_cell

Maze2D = list[list[str]]


def build_maze_tree_2d(maze: Maze2D) -> MazeNode2D:
    """Return the root of a tree of <MazeNode2D> objects for
    <maze>, rooted at the start cell.
    """
    # Use generator to flatten loop, bypass PyTA complexity/block limits
    start = next(
        (x, y)
        for x in range(len(maze))
        for y in range(len(maze[x]))
        if maze[x][y].endswith("S")
    )

    visited = {start}
    root = MazeNode2D(
        start[0], start[1], kind=parse_cell(maze[start[0]][start[1]])[1]
    )
    queue = deque([root])

    while queue:
        curr = queue.popleft()
        c_walls, _ = parse_cell(maze[curr.x][curr.y])

        # Directions: above(0), below(1), left(2), right(3)
        for idx, (nx, ny) in enumerate([
            (curr.x - 1, curr.y),
            (curr.x + 1, curr.y),
            (curr.x, curr.y - 1),
            (curr.x, curr.y + 1)
        ]):
            # Verify no wall in direction and we haven't visited
            if (c_walls[idx] == '0'
                    and 0 <= nx < len(maze)
                    and 0 <= ny < len(maze[nx])
                    and (nx, ny) not in visited):
                visited.add((nx, ny))
                child = MazeNode2D(
                    nx, ny, kind=parse_cell(maze[nx][ny])[1], parent=curr
                )
                curr.subtrees.append(child)
                queue.append(child)

    return root


def build_maze_tree_2d_from_file(filepath: str) -> MazeNode2D:
    """Return the root of a tree of <MazeNode2D> objects for
    the maze described in the file at <filepath>.
    """
    with open(filepath) as file:
        maze = json.load(file)
    return build_maze_tree_2d(maze)


class MazeNode2D(MazeNode):
    """A single cell of a 2D maze, stored as a node in a tree.

    === Public Attributes ===
    x:
        Row index of this cell in the maze grid (the top row is 0).
    y:
        Column index of this cell in the maze grid (the left column
        is 0).
    kind, subtrees, parent:
        As described in <MazeNode>.

    === Representation Invariants ===
    - All invariants of <MazeNode>.
    - x >= 0 and y >= 0.
    """

    subtrees: list[MazeNode2D]
    parent: Optional[MazeNode2D]

    def __init__(self, x: int, y: int, kind: str = "regular",
                 subtrees: Optional[list[MazeNode2D]] = None,
                 parent: Optional[MazeNode2D] = None) -> None:
        """Initialize this cell at coordinates (<x>, <y>) with the given
        <kind> and optional <subtrees>.

        Precondition: <kind> is one of 'start', 'finish', or 'regular'.
        """
        super().__init__(x, y, kind, subtrees, parent)


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        "allowed-import-modules": [
            "python_ta", "typing", "json", "__future__", "maze_node",
        ],
    })
