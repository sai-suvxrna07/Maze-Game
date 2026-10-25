"""Assignment 2

=== UTM CSC148 Summer 2026 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto
Mississauga. Copying for purposes other than this use is expressly
prohibited. All forms of distribution of this code, whether as given
or with any changes, are expressly prohibited.

=== Module Description ===
This file is where you will add your own test cases that you will submit on MarkUs.
"""

import pytest

import pytest
from maze_node import MazeNode
from maze_2d import MazeNode2D, build_maze_tree_2d
from maze_3d import MazeNode3D, build_maze_tree_3d

import sys
import random

# Helper maze samples based on the starter file
HORIZ_2 = [["1110S", "1101F"]]
SQUARE_2X2 = [
    ["1010S", "1001"],
    ["0111", "0111F"]
]
X_2_3D = [
    [["011111S"]],
    [["101111F"]],
]


def test_maze_node_init():
    """Test standard MazeNode initialization."""
    node = MazeNode(1, 2, kind="start")
    assert node.x == 1
    assert node.y == 2
    assert node.kind == "start"
    assert node.parent is None
    assert node.subtrees == []


def test_maze_node_init_with_subtrees():
    """Test MazeNode properly setting itself as parent for subtrees."""
    child1 = MazeNode(2, 2)
    child2 = MazeNode(3, 3)
    parent_node = MazeNode(1, 1, subtrees=[child1, child2])
    assert child1.parent == parent_node
    assert child2.parent == parent_node
    assert len(parent_node.subtrees) == 2


def test_maze_node2d_init():
    """Test MazeNode2D subclass initialization."""
    node = MazeNode2D(5, 6, kind="finish")
    assert node.x == 5
    assert node.y == 6
    assert node.kind == "finish"
    assert isinstance(node, MazeNode)


def test_maze_node3d_init():
    """Test MazeNode3D subclass initialization."""
    node = MazeNode3D(1, 2, 3, kind="start")
    assert node.x == 1
    assert node.y == 2
    assert node.z == 3
    assert node.kind == "start"
    assert isinstance(node, MazeNode)


def test_build_maze_tree_2d():
    """Test 2D maze tree construction properly links subtrees."""
    root = build_maze_tree_2d(HORIZ_2)
    assert root.x == 0 and root.y == 0
    assert root.kind == "start"
    assert len(root.subtrees) == 1

    child = root.subtrees[0]
    assert child.x == 0 and child.y == 1
    assert child.kind == "finish"
    assert child.parent == root


def test_build_maze_tree_3d():
    """Test 3D maze tree construction properly links subtrees via z-dimension string."""
    root = build_maze_tree_3d(X_2_3D)
    assert root.x == 0 and root.y == 0 and root.z == 0
    assert root.kind == "start"
    assert len(root.subtrees) == 1

    child = root.subtrees[0]
    assert child.x == 1 and child.y == 0 and child.z == 0
    assert child.kind == "finish"
    assert child.parent == root


def test_get_root():
    """Test returning the origin parent of a nested chain."""
    root = MazeNode2D(0, 0, kind="start")
    child1 = MazeNode2D(0, 1, parent=root)
    child2 = MazeNode2D(0, 2, parent=child1)

    assert child2.get_root() == root
    assert root.get_root() == root


def test_make_start():
    """Test re-rooting the tree to a newly designated start point."""
    root = build_maze_tree_2d(HORIZ_2)
    finish_node = root.subtrees[0]

    # Reroot to the finish node
    finish_node.make_start()

    assert finish_node.kind == 'start'
    assert root.kind == 'regular'
    assert finish_node.parent is None
    assert root.parent == finish_node
    assert root in finish_node.subtrees


def test_make_finish():
    """Test assigning a new finish node removes the old one."""
    root = build_maze_tree_2d(HORIZ_2)

    # Set the root itself to finish
    root.make_finish()

    assert root.kind == 'finish'
    assert root.subtrees[0].kind == 'regular'


def test_preorder_solve():
    """Test finding path using DFS (preorder)."""
    root = build_maze_tree_2d(SQUARE_2X2)
    path = root.preorder_solve()

    # Path should trace from S(0,0) -> (0,1) -> (1,1)
    assert len(path) == 3
    assert path[0].kind == "start"
    assert path[-1].kind == "finish"
    assert path[0].x == 0 and path[0].y == 0
    assert path[1].x == 0 and path[1].y == 1
    assert path[2].x == 1 and path[2].y == 1


def test_levelorder_solve():
    """Test finding path using BFS (level-order)."""
    root = build_maze_tree_2d(SQUARE_2X2)
    path = root.levelorder_solve()

    # Path should trace from S(0,0) -> (0,1) -> (1,1)
    assert len(path) == 3
    assert path[0].kind == "start"
    assert path[-1].kind == "finish"
    assert path[0].x == 0 and path[0].y == 0
    assert path[1].x == 0 and path[1].y == 1
    assert path[2].x == 1 and path[2].y == 1


# ==========================================
# TEST MAZES
# ==========================================

# 2D: A maze with a dead end to trick preorder_solve.
# Path goes right, but there's a dead end going down.
DEAD_END_2D = [
    ["1010S", "1100", "1101F"],
    ["0111", "1111", "1111"]
]

# 3D: A vertical shaft (movement entirely on the Z-axis)
VERTICAL_SHAFT_3D = [
    [
        ["111101S", "111100", "111110F"]
    ]
]


# ==========================================
# CORE NODE TESTS (maze_node.py)
# ==========================================

def test_make_start_already_start():
    """Test make_start does nothing if the node is already start."""
    root = MazeNode(0, 0, kind='start')
    child = MazeNode(0, 1, parent=root)
    root.subtrees.append(child)

    root.make_start()  # Should be a no-op

    assert root.kind == 'start'
    assert child.kind == 'regular'
    assert root.parent is None
    assert child.parent == root


def test_make_finish_already_finish():
    """Test make_finish does nothing if the node is already finish."""
    root = MazeNode(0, 0, kind='start')
    child = MazeNode(0, 1, kind='finish', parent=root)
    root.subtrees.append(child)

    child.make_finish()  # Should be a no-op

    assert child.kind == 'finish'
    assert len(root.subtrees) == 1


def test_make_start_deep_chain():
    """Test re-rooting from deep within a straight line."""
    node_a = MazeNode(0, 0, kind="start")
    node_b = MazeNode(0, 1, parent=node_a)
    node_c = MazeNode(0, 2, parent=node_b)
    node_a.subtrees.append(node_b)
    node_b.subtrees.append(node_c)

    # Reroot to C
    node_c.make_start()

    assert node_c.kind == 'start'
    assert node_a.kind == 'regular'

    # Check new parent/child relationships
    assert node_c.parent is None
    assert node_b in node_c.subtrees
    assert node_b.parent == node_c
    assert node_a in node_b.subtrees
    assert node_a.parent == node_b
    assert len(node_a.subtrees) == 0





def test_build_maze_dead_end_visited_logic():
    """Ensure the builder doesn't visit cells twice or go through walls."""
    root = build_maze_tree_2d(DEAD_END_2D)

    # Root (0,0) should have TWO children: (0,1) and (1,0)
    assert len(root.subtrees) == 2

    # Check coords of children
    coords = {(child.x, child.y) for child in root.subtrees}
    assert coords == {(0, 1), (1, 0)}


# ==========================================
# 3D MAZE TESTS (maze_3d.py)
# ==========================================

def test_build_maze_vertical_shaft():
    """Test traversing the z-axis exclusively."""
    root = build_maze_tree_3d(VERTICAL_SHAFT_3D)

    assert root.x == 0 and root.y == 0 and root.z == 0
    assert len(root.subtrees) == 1

    child = root.subtrees[0]
    # Check that we moved along Z, not X
    assert child.x == 0 and child.y == 0 and child.z == 1

    grandchild = child.subtrees[0]
    assert grandchild.kind == 'finish'
    assert grandchild.x == 0 and grandchild.y == 0 and grandchild.z == 2


# ==========================================
# SOLVING ALGORITHM TESTS
# ==========================================

def test_preorder_solve_avoids_dead_ends():
    """DFS must pop dead ends off the path before returning."""
    root = build_maze_tree_2d(DEAD_END_2D)
    path = root.preorder_solve()

    # Path should go (0,0) -> (0,1) -> (0,2).
    # It should NOT contain (1,0) even though it's connected to (0,0).
    path_coords = [(n.x, n.y) for n in path]
    assert path_coords == [(0, 0), (0, 1), (0, 2)]
    assert (1, 0) not in path_coords


def test_levelorder_solve_avoids_dead_ends():
    """BFS must correctly trace parent pointers back from the finish node."""
    root = build_maze_tree_2d(DEAD_END_2D)
    path = root.levelorder_solve()

    path_coords = [(n.x, n.y) for n in path]
    assert path_coords == [(0, 0), (0, 1), (0, 2)]
    assert (1, 0) not in path_coords


def generate_long_corridor_2d(length: int) -> list[list[str]]:
    """Generates a 1D corridor of specified length to test recursion depth."""
    maze = []
    row = []
    # Start node (walls above, below, left)
    row.append("1110S")
    # Middle nodes (walls above, below)
    for _ in range(length - 2):
        row.append("1100")
    # Finish node (walls above, below, right)
    row.append("1101F")
    maze.append(row)
    return maze


def get_all_nodes_2d(root: MazeNode2D) -> list[MazeNode2D]:
    """Helper to flatten the tree into a list of nodes for random sampling."""
    nodes = []
    queue = [root]
    while queue:
        curr = queue.pop(0)
        nodes.append(curr)
        queue.extend(curr.subtrees)
    return nodes


def test_deep_recursion_corridor():
    """
    TEST 3: Very long corridor.
    Forces preorder_solve (DFS) to recurse 2000+ times.
    """
    # Increase Python's default recursion limit (usually 1000) to prevent a crash on valid deep trees
    sys.setrecursionlimit(5000)

    corridor_length = 2500
    maze = generate_long_corridor_2d(corridor_length)
    root = build_maze_tree_2d(maze)

    # DFS should be able to reach the end without blowing the stack
    path = root.preorder_solve()

    assert len(path) == corridor_length
    assert path[0].kind == 'start'
    assert path[-1].kind == 'finish'


def test_fuzz_mutations_and_solvers():
    """
    TEST 5, 6, 7, 8: The Fuzzer.
    Builds a 2x2 grid, then randomly hammers make_start and make_finish
    1000 times, verifying invariants and solving algorithms after each batch.
    """
    # Using SQUARE_2X2 from the top of the file
    root = build_maze_tree_2d(SQUARE_2X2)

    for _ in range(100):  # 100 batches of mutations
        all_nodes = get_all_nodes_2d(root.get_root())

        # 1. Randomly assign a new start
        new_start = random.choice(all_nodes)
        new_start.make_start()

        # 2. Randomly assign a new finish (Must be DISTINCT from start)
        available_for_finish = [n for n in all_nodes if n != new_start]
        new_finish = random.choice(available_for_finish)
        new_finish.make_finish()

        # 3. Verify Invariants
        current_root = new_start.get_root()
        assert current_root.kind == 'start', "Root must always be the start node."

        # Count starts and finishes
        starts = [n for n in all_nodes if n.kind == 'start']
        finishes = [n for n in all_nodes if n.kind == 'finish']

        assert len(starts) == 1, f"Expected 1 start, found {len(starts)}"
        assert len(finishes) == 1, f"Expected 1 finish, found {len(finishes)}"

        # 4. Verify Solvers
        pre_path = current_root.preorder_solve()
        lvl_path = current_root.levelorder_solve()

        assert len(pre_path) > 0, "Preorder failed to find a path."
        assert len(lvl_path) > 0, "Levelorder failed to find a path."
        assert pre_path[0].kind == 'start' and pre_path[-1].kind == 'finish'
        assert lvl_path[0].kind == 'start' and lvl_path[-1].kind == 'finish'
