"""Assignment 2: Maze Trees — 3-D mazes

=== UTM CSC148 Summer 2026 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto
Mississauga. Copying for purposes other than this use is expressly
prohibited. All forms of distribution of this code, whether as given
or with any changes, are expressly prohibited.

=== Module Description ===
This module defines the <MazeNode3D> subclass and the helper
functions needed to build a 3-D maze as a tree of cells.

A 3D maze extends the 2D <Maze2D> format with a third dimension,
which you can think of as height: there are multiple floors, and
adjacent floors are only connected by stairs at certain points. It is
represented as a rectangular list of lists of lists of
strings, where each cell's string follows the same format as in
<maze_2d>, except that instead of 4 binary digits it starts with 6,
each representing whether there is a wall separating it from the cell
at (x+1, y, z), (x-1, y, z), (x, y+1, z), (x, y-1, z), (x, y, z+1),
or (x, y, z-1) respectively. An 'S' suffix marks the start cell and
an 'F' suffix marks the finish cell.
    - a maze is always surrounded by walls on its borders.
"""
from __future__ import annotations

import json
from typing import Optional

from maze_node import MazeNode, parse_cell

Maze3D = list[list[list[str]]]



def build_maze_tree_3d(maze: Maze3D) -> MazeNode3D:
    """Return the root of a tree of <MazeNode3D> objects for
    <maze>, rooted at the start cell.
    """
    # TODO: TASK 5: implement this!
    #       be careful here. read the handout carefully to understand
    #       how the 3D maze format works.
    pass

def build_maze_tree_3d_from_file(filepath: str) -> MazeNode3D:
    """Return the root of a tree of <MazeNode3D> objects for
    the maze described in the file at <filepath>.
    """
    with open(filepath) as file:
        maze = json.load(file)
    return build_maze_tree_3d(maze)


class MazeNode3D(MazeNode):
    """A single cell of a 3-D maze, stored as a node in a tree.

    === Public Attributes ===
    x, y, z:
        Grid coordinates of this cell in the maze.
    kind, subtrees, parent:
        As described in <MazeNode>.

    === Representation Invariants ===
    - All invariants of <MazeNode>.
    - x >= 0, y >= 0, and z >= 0.
    """
    z: int
    subtrees: list[MazeNode3D]
    parent: Optional[MazeNode3D]

    def __init__(self, x: int, y: int, z: int = 0, kind: str = "regular",
                 subtrees: Optional[list[MazeNode3D]] = None,
                 parent: Optional[MazeNode3D] = None) -> None:
        """Initialize this cell at coordinates (<x>, <y>, <z>) with the
        given <kind> and optional <subtrees>.

        Precondition: <kind> is one of 'start', 'finish', or 'regular'.
        """
        # TODO: TASK 3: implement this!
        pass

if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        "allowed-import-modules": [
            "python_ta", "typing", "json", "__future__", "maze_node",
        ],
    })
