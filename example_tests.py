from __future__ import annotations

import pytest

from maze_2d import (
    Maze2D,
    MazeNode2D,
    build_maze_tree_2d,
)
from maze_3d import (
    Maze3D,
    MazeNode3D,
    build_maze_tree_3d,
)


# NOTE: These are intentionally just a few examples (not a full test suite).
# Add your own tests to check more edge cases and larger mazes.


def _path_positions_2d(path: list[MazeNode2D]) -> list[tuple[int, int]]:
    """Return [(x, y), ...] for nodes in <path>."""
    return [(n.x, n.y) for n in path]


def _path_positions_3d(path: list[MazeNode3D]) -> list[tuple[int, int, int]]:
    """Return [(x, y, z), ...] for nodes in <path>."""
    return [(n.x, n.y, n.z) for n in path]


def _iter_nodes_2d(root: MazeNode2D) -> list[MazeNode2D]:
    """Return every node in the tree rooted at <root>."""
    out = [root]
    for subtree in root.subtrees:
        out.extend(_iter_nodes_2d(subtree))
    return out


# ---------------------------------------------------------------------------
# Small sample mazes used in this starter test file
#
# Wall digits: above, below, left, right (see handout / maze_2d.py).
# Outward-facing sides on the grid border use 1 (wall).
# ---------------------------------------------------------------------------

# 2D: one row, two cells (start -> finish)
HORIZ_2: Maze2D = [["1110S", "1101F"]]

# 2D: one row, four cells with finish in the middle
# S - R - F - R
CORRIDOR_4_FINISH_MIDDLE: Maze2D = [
    ["1110S", "1100", "1100F", "1101"]
]

# 3D: two cells connected along the x-axis
X_2: Maze3D = [
    [["011111S"]],
    [["101111F"]],
]


class TestExample2D:
    def test_build_tree_root_is_start(self) -> None:
        root = build_maze_tree_2d(HORIZ_2)
        assert (root.x, root.y) == (0, 0)
        assert root.kind == "start"

    def test_preorder_solve_simple_path(self) -> None:
        root = build_maze_tree_2d(HORIZ_2)
        assert _path_positions_2d(root.preorder_solve()) == [(0, 0), (0, 1)]

    def test_make_finish_replaces_old_finish(self) -> None:
        root = build_maze_tree_2d(CORRIDOR_4_FINISH_MIDDLE)

        # In this sample, (0, 3) is reachable and not initially finish.
        new_finish = [n for n in _iter_nodes_2d(root) if (n.x, n.y) == (0, 3)][0]
        new_finish.make_finish()

        finish_nodes = [n for n in _iter_nodes_2d(root) if n.kind == "finish"]
        assert len(finish_nodes) == 1
        assert finish_nodes[0] is new_finish


class TestExample3D:
    def test_preorder_solve_x_pair(self) -> None:
        root = build_maze_tree_3d(X_2)
        assert _path_positions_3d(root.preorder_solve()) == [(0, 0, 0), (1, 0, 0)]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])