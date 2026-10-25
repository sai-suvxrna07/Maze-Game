from maze_2d import MazeNode2D, build_maze_tree_2d_from_file
from maze_3d import MazeNode3D, build_maze_tree_3d_from_file
from maze_node import MazeNode

from itertools import product
import pygame
import sys
from dataclasses import dataclass

# dimension agnostic types for rank-polymorphic code
Vector = tuple[int, int] | tuple[int, int, int]


def pos_vector(node: MazeNode) -> Vector:
    """Return the position vector of a MazeNode."""
    return (node.x, node.y) if isinstance(node, MazeNode2D) else (node.x, node.y, node.z)


neighbor_dirs = {
    2: [(-1, 0), (1, 0), (0, -1), (0, 1)],
    3: [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)],
}

UP, DOWN, LEFT, RIGHT = neighbor_dirs[2]
UP3, DOWN3, LEFT3, RIGHT3, BELOW3, ABOVE3 = neighbor_dirs[3]

@dataclass
class MazeCell:
    # (x, y) for 2d, (x, y, z) for 3d
    coords: Vector
    
    kind: str # "start", "finish", or "regular"

    # indexed by direction vector to indicate whether there is a wall in that direction
    # there is a wall between u and v iff u.walls[v.coords - u.coords] is True
    walls: dict[Vector, bool]


@dataclass
class Maze:
    dims: Vector
    cells: list[MazeCell]


def compute_description(maze: MazeNode) -> Maze:
    """
    Compute a description of the maze in terms of its dimensions and the walls between cells.
    """

    coordmap: dict[Vector, MazeNode] = {}
    def make_coordinate_map(node: MazeNode):
        coordmap[pos_vector(node)] = node
        for subnode in node.subtrees:
            make_coordinate_map(subnode)

    # cells are neighbors iff they are adjacent in the tree iff one is a subtree of the other
    def are_neighbors(c1: Vector, c2: Vector):
        m1 = coordmap.get(c1)
        m2 = coordmap.get(c2)

        return m1 is not None and m2 is not None and (
            m1 in m2.subtrees or m2 in m1.subtrees
        )
    
    make_coordinate_map(maze)

    dimension = 2 if isinstance(maze, MazeNode2D) else 3

    dims = tuple(1 + max(c[i] for c in coordmap) for i in range(dimension))
    
    cells = []
    for coords in product(*(range(d) for d in dims)):
        # cells that are not in the coordinate map are unreachable from start node
        # so treat them as having walls on all sides
        if coords not in coordmap:
            cells.append(MazeCell(coords, "regular", {d: True for d in neighbor_dirs[dimension]}))
            continue
        
        walls = {
            d: not are_neighbors(coords, tuple(ci + di for ci, di in zip(coords, d)))
            for d in neighbor_dirs[dimension]
        }

        cell = MazeCell(coords, coordmap[coords].kind, walls)
        cells.append(cell)

    return Maze(dims, cells)


def render_ascii(maze: MazeNode2D) -> str:
    """Return a multi-line ASCII string that depicts the maze.
    
    Walls are drawn with '+', '-', and '|'; the interior of start/finish cells are
    labelled 'S' and 'F'; all other cell interiors use a space.

    Example output for a 2x2 maze::
 
        +--+--+
        |S    |
        +  +--+
        |   F |
        +--+--+
    """
    desc = compute_description(maze)
    assert len(desc.dims) == 2, "error: render_ascii only supports 2d mazes"
    h, w = desc.dims
 
    # each cell is 2 characters wide and 1 character tall, and there is a border of walls around the whole maze.
    rows = 2 * h + 1
    cols = 3 * w + 1
    grid: list[list[str]] = [[" "] * cols for _ in range(rows)]
    
    # add the '+' characters for all corners 
    for r in range(h + 1):
        for c in range(w + 1):
            grid[2 * r][3 * c] = "+"
 
    for mc in desc.cells:
        x, y = mc.coords
        cr = 2 * x + 1   # character row of cell interior
        cc = 3 * y + 1   # beginning col of cell interior
 
        if mc.kind == "start":
            grid[cr][cc] = "S"
        elif mc.kind == "finish":
            grid[cr][cc] = "F"

        # horizontal walls are two characters wide
        if mc.walls[UP]:
            grid[cr - 1][cc] = "-"
            grid[cr - 1][cc + 1] = "-"
        
        if mc.walls[DOWN]:
            grid[cr + 1][cc] = "-"
            grid[cr + 1][cc + 1] = "-"

        if mc.walls[LEFT]:
            grid[cr][cc - 1] = "|"

        if mc.walls[RIGHT]:
            grid[cr][cc + 2] = "|"
 
    return "\n".join("".join(row) for row in grid)
 
 
def render_pygame2d(maze: MazeNode2D, cell_size: int = 60) -> None:
    """Open a fixed-size pygame window and draw the maze.

    The viewport is fixed at 1000x1000 pixels. For mazes larger than the
    viewport, the view can be panned by:
      - Clicking and dragging with the middle mouse button, OR
      - Holding Shift and using the arrow keys.

    A player character (yellow circle) starts at the 'start' cell and can
    be moved with WASD or the arrow keys. Movement is blocked by walls.
    The camera automatically re-centres on the player whenever they move.

    Each cell is a square of side *cell_size* pixels. Walls are drawn
    as thick lines. The start cell is tinted green and the finish cell
    is tinted red. The window stays open until the user closes it.
    """
    desc = compute_description(maze)
    assert len(desc.dims) == 2, "error: render_pygame2d only supports 2d mazes"
    h, w = desc.dims

    WALL_COLOR   = (30,  30,  30)
    BG_COLOR     = (245, 245, 245)
    START_COLOR  = (120, 210, 130)
    FINISH_COLOR = (210, 100, 100)
    TEXT_COLOR   = (255, 255, 255)
    PLAYER_COLOR = (255, 210,  50)
    PLAYER_BORDER= (180, 140,  10)
    WALL_WIDTH   = 3
    PADDING      = 20

    VIEWPORT_W   = 1000
    VIEWPORT_H   = 1000

    # Build a lookup table for fast wall queries
    cellmap: dict[tuple, MazeCell] = {mc.coords: mc for mc in desc.cells}

    # Locate start cell for initial player position
    start_coords = next(
        (mc.coords for mc in desc.cells if mc.kind == "start"),
        (0, 0),
    )
    player: list[int] = list(start_coords)   # mutable [x, y]

    # Camera offset: top-left corner of the viewport in maze-pixel space
    total_w = w * cell_size + 2 * PADDING
    total_h = h * cell_size + 2 * PADDING
    cam: list[float] = [0.0, 0.0]  # [cam_x (horizontal), cam_y (vertical)]

    def clamp_camera() -> None:
        cam[0] = max(0.0, min(cam[0], max(0.0, total_w  - VIEWPORT_W)))
        cam[1] = max(0.0, min(cam[1], max(0.0, total_h - VIEWPORT_H)))

    def centre_camera_on_player() -> None:
        px, py = player
        # pixel centre of player cell
        pcx = PADDING + py * cell_size + cell_size // 2
        pcy = PADDING + px * cell_size + cell_size // 2
        cam[0] = pcx - VIEWPORT_W / 2
        cam[1] = pcy - VIEWPORT_H / 2
        clamp_camera()

    centre_camera_on_player()

    def cell_rect(x: int, y: int) -> pygame.Rect:
        """Return the on-screen pygame.Rect for cell (x, y) given current camera."""
        return pygame.Rect(
            PADDING + y * cell_size - int(cam[0]),
            PADDING + x * cell_size - int(cam[1]),
            cell_size,
            cell_size,
        )

    pygame.init()
    screen = pygame.display.set_mode((VIEWPORT_W, VIEWPORT_H))
    pygame.display.set_caption("Maze  [Arrow/WASD = move  |  Shift+Arrow / MMB drag = pan]")
    font = pygame.font.SysFont(None, cell_size // 2)
    font_hud = pygame.font.SysFont(None, 20)

    # --- middle-mouse pan state ---
    mmb_dragging = False
    mmb_last: tuple[int, int] = (0, 0)

    won = False
    win_timer = 0   # frames to display the win flash

    PAN_SPEED = 15  # pixels per frame when panning with Shift+Arrow

    # Directions for player movement: key -> (dx, dy) in cell coords, wall key
    MOVE_KEYS: dict[int, tuple[tuple[int, int], tuple[int, int]]] = {
        pygame.K_UP:    (UP,    UP),
        pygame.K_w:     (UP,    UP),
        pygame.K_DOWN:  (DOWN,  DOWN),
        pygame.K_s:     (DOWN,  DOWN),
        pygame.K_LEFT:  (LEFT,  LEFT),
        pygame.K_a:     (LEFT,  LEFT),
        pygame.K_RIGHT: (RIGHT, RIGHT),
        pygame.K_d:     (RIGHT, RIGHT),
    }

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                shift = mods & pygame.KMOD_SHIFT

                if event.key in MOVE_KEYS and not shift:
                    # --- player movement ---
                    (dx, dy), wall_dir = MOVE_KEYS[event.key]
                    cur = cellmap.get(tuple(player))
                    if cur and not cur.walls[wall_dir]:
                        player[0] += dx
                        player[1] += dy
                        centre_camera_on_player()
                        # Check win condition
                        dest = cellmap.get(tuple(player))
                        if dest and dest.kind == "finish":
                            won = True
                            win_timer = 120  # ~2 s at 60 fps

                elif event.key in (pygame.K_UP, pygame.K_w) and shift:
                    cam[1] -= PAN_SPEED; clamp_camera()
                elif event.key in (pygame.K_DOWN, pygame.K_s) and shift:
                    cam[1] += PAN_SPEED; clamp_camera()
                elif event.key in (pygame.K_LEFT, pygame.K_a) and shift:
                    cam[0] -= PAN_SPEED; clamp_camera()
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and shift:
                    cam[0] += PAN_SPEED; clamp_camera()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                mmb_dragging = True
                mmb_last = event.pos
            # Touchpad/scroll wheel (legacy buttons)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5, 6, 7):
                if event.button == 4:   # wheel up
                    cam[1] -= PAN_SPEED
                elif event.button == 5: # wheel down
                    cam[1] += PAN_SPEED
                elif event.button == 6: # wheel left
                    cam[0] -= PAN_SPEED
                elif event.button == 7: # wheel right
                    cam[0] += PAN_SPEED
                clamp_camera()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                mmb_dragging = False
            # Touchpad/scroll wheel (pygame 2+)
            elif event.type == pygame.MOUSEWHEEL:
                cam[0] -= event.x * PAN_SPEED
                cam[1] -= event.y * PAN_SPEED
                clamp_camera()
            elif event.type == pygame.MOUSEMOTION and mmb_dragging:
                dx = event.pos[0] - mmb_last[0]
                dy = event.pos[1] - mmb_last[1]
                cam[0] -= dx
                cam[1] -= dy
                clamp_camera()
                mmb_last = event.pos

        # --- draw ---
        screen.fill(BG_COLOR)

        for mc in desc.cells:
            x, y = mc.coords
            rect = cell_rect(x, y)

            # Skip cells entirely outside the viewport
            if rect.right < 0 or rect.left > VIEWPORT_W:
                continue
            if rect.bottom < 0 or rect.top > VIEWPORT_H:
                continue

            if mc.kind == "start":
                pygame.draw.rect(screen, START_COLOR, rect)
                lbl = font.render("S", True, TEXT_COLOR)
                screen.blit(lbl, lbl.get_rect(center=rect.center))
            elif mc.kind == "finish":
                pygame.draw.rect(screen, FINISH_COLOR, rect)
                lbl = font.render("F", True, TEXT_COLOR)
                screen.blit(lbl, lbl.get_rect(center=rect.center))

            x0, y0 = rect.left, rect.top
            x1, y1 = rect.right, rect.bottom
            if mc.walls[UP]:
                pygame.draw.line(screen, WALL_COLOR, (x0, y0), (x1, y0), WALL_WIDTH)
            if mc.walls[DOWN]:
                pygame.draw.line(screen, WALL_COLOR, (x0, y1), (x1, y1), WALL_WIDTH)
            if mc.walls[LEFT]:
                pygame.draw.line(screen, WALL_COLOR, (x0, y0), (x0, y1), WALL_WIDTH)
            if mc.walls[RIGHT]:
                pygame.draw.line(screen, WALL_COLOR, (x1, y0), (x1, y1), WALL_WIDTH)

        # Draw player
        prect = cell_rect(player[0], player[1])
        radius = cell_size // 3
        pygame.draw.circle(screen, PLAYER_BORDER, prect.center, radius + 2)
        pygame.draw.circle(screen, PLAYER_COLOR,  prect.center, radius)

        # Win overlay
        if won and win_timer > 0:
            win_timer -= 1
            overlay = pygame.Surface((VIEWPORT_W, VIEWPORT_H), pygame.SRCALPHA)
            alpha = min(180, win_timer * 3)
            overlay.fill((255, 215, 0, alpha))
            screen.blit(overlay, (0, 0))
            msg = font.render("You reached the finish!", True, (80, 40, 0))
            screen.blit(msg, msg.get_rect(center=(VIEWPORT_W // 2, VIEWPORT_H // 2)))

        # HUD
        hud = font_hud.render(
            "Arrow/WASD: move    Shift+Arrow or MMB drag: pan",
            True, (100, 100, 100),
        )
        screen.blit(hud, (8, VIEWPORT_H - 22))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def render_pygame3d(maze: MazeNode3D, cell_size: int = 50) -> None:
    """Open a fixed-size pygame window and draw the 3-D maze floor by floor.

    The viewport is fixed at 1000x1000 pixels. For mazes larger than the
    viewport, the view can be panned by clicking and dragging with the middle
    mouse button, or by holding Shift and pressing the arrow keys.

    A player character (yellow circle) starts at the 'start' cell. Controls:
      Arrow keys / WASD     — move within the current floor (N/S/E/W)
      Q / E                 — climb down / climb up between floors (only when
                              the cell has a passage in that direction)
      Shift + Arrow / MMB   — pan the camera

    Each floor (z-slice) is drawn as a 2-D grid. Floors are stacked vertically
    on screen from z=0 (bottom) to z=max (top), separated by labelled dividers.
    Cells with an open passage upward show a blue ▲; cells with a passage
    downward show an orange ▼.
    """
    desc = compute_description(maze)
    assert len(desc.dims) == 3, "error: render_pygame3d only supports 3d mazes"
    rows, cols, floors = desc.dims

    WALL_COLOR    = (30,  30,  30)
    BG_COLOR      = (245, 245, 245)
    START_COLOR   = (120, 210, 130)
    FINISH_COLOR  = (210, 100, 100)
    TEXT_COLOR    = (255, 255, 255)
    PLAYER_COLOR  = (255, 210,  50)
    PLAYER_BORDER = (180, 140,  10)
    DIVIDER_COLOR = (180, 180, 220)
    DIVIDER_TEXT  = (60,  60,  120)
    STAIR_UP_CLR  = (70,  130, 200)
    STAIR_DN_CLR  = (200, 130,  70)
    WALL_WIDTH    = 3
    PADDING       = 20
    DIVIDER_H     = 28

    VIEWPORT_W    = 1000
    VIEWPORT_H    = 1000

    floor_h  = rows * cell_size
    content_h = floors * floor_h + (floors - 1) * DIVIDER_H
    # Center grid horizontally if viewport is wider than the grid
    PADDING_X = max(PADDING, (VIEWPORT_W - cols * cell_size) // 2)
    # Center entire stack vertically if viewport is taller than content
    PADDING_Y = max(PADDING, (VIEWPORT_H - content_h) // 2)
    total_w  = cols * cell_size + 2 * PADDING_X
    total_h  = content_h + 2 * PADDING_Y

    cellmap: dict[tuple, MazeCell] = {mc.coords: mc for mc in desc.cells}

    start_coords = next(
        (mc.coords for mc in desc.cells if mc.kind == "start"),
        (0, 0, 0),
    )
    player: list[int] = list(start_coords)  # [x, y, z]

    cam: list[float] = [0.0, 0.0]

    def floor_top_y_world(z: int) -> int:
        return PADDING_Y + z * (floor_h + DIVIDER_H)

    def clamp_camera() -> None:
        cam[0] = max(0.0, min(cam[0], max(0.0, total_w  - VIEWPORT_W)))
        cam[1] = max(0.0, min(cam[1], max(0.0, total_h - VIEWPORT_H)))

    def centre_camera_on_player() -> None:
        px, py, pz = player
        pcx = PADDING_X + py * cell_size + cell_size // 2
        pcy = floor_top_y_world(pz) + px * cell_size + cell_size // 2
        cam[0] = pcx - VIEWPORT_W / 2
        cam[1] = pcy - VIEWPORT_H / 2
        clamp_camera()

    centre_camera_on_player()

    def cell_rect(x: int, y: int, z: int) -> pygame.Rect:
        return pygame.Rect(
            PADDING_X + y * cell_size - int(cam[0]),
            floor_top_y_world(z) + x * cell_size - int(cam[1]),
            cell_size,
            cell_size,
        )

    def draw_stair_triangle(surf, rect, direction, color) -> None:
        cx, cy = rect.centerx, rect.centery
        s = cell_size // 6
        h = cell_size // 5
        if direction == "up":
            cx -= cell_size // 5
            pts = [(cx, cy - h), (cx - s, cy + h // 2), (cx + s, cy + h // 2)]
        else:
            cx += cell_size // 5
            pts = [(cx, cy + h), (cx - s, cy - h // 2), (cx + s, cy - h // 2)]
        pygame.draw.polygon(surf, color, pts)

    pygame.init()
    screen = pygame.display.set_mode((VIEWPORT_W, VIEWPORT_H))
    pygame.display.set_caption(
        "Maze 3D  [Arrow/WASD=move  Q/E=down/up  Scroll/Shift+Arrow/MMB=pan]"
    )
    font_cell  = pygame.font.SysFont(None, cell_size // 2)
    font_label = pygame.font.SysFont(None, DIVIDER_H - 4)
    font_hud   = pygame.font.SysFont(None, 20)

    mmb_dragging = False
    mmb_last: tuple[int, int] = (0, 0)

    won = False
    win_timer = 0

    PAN_SPEED = 15

    MOVE_KEYS = {
        pygame.K_UP:    UP3,
        pygame.K_w:     UP3,
        pygame.K_DOWN:  DOWN3,
        pygame.K_s:     DOWN3,
        pygame.K_LEFT:  LEFT3,
        pygame.K_a:     LEFT3,
        pygame.K_RIGHT: RIGHT3,
        pygame.K_d:     RIGHT3,
    }

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                shift = mods & pygame.KMOD_SHIFT

                if event.key in MOVE_KEYS and not shift:
                    direction = MOVE_KEYS[event.key]
                    cur = cellmap.get(tuple(player))
                    if cur and not cur.walls[direction]:
                        player[0] += direction[0]
                        player[1] += direction[1]
                        # z component is 0 for lateral moves
                        centre_camera_on_player()
                        dest = cellmap.get(tuple(player))
                        if dest and dest.kind == "finish":
                            won = True; win_timer = 120

                elif event.key == pygame.K_e and not shift:
                    # climb up (z increases)
                    cur = cellmap.get(tuple(player))
                    if cur and not cur.walls[ABOVE3]:
                        player[2] += 1
                        centre_camera_on_player()
                        dest = cellmap.get(tuple(player))
                        if dest and dest.kind == "finish":
                            won = True; win_timer = 120

                elif event.key == pygame.K_q and not shift:
                    # climb down (z decreases)
                    cur = cellmap.get(tuple(player))
                    if cur and not cur.walls[BELOW3]:
                        player[2] -= 1
                        centre_camera_on_player()
                        dest = cellmap.get(tuple(player))
                        if dest and dest.kind == "finish":
                            won = True; win_timer = 120

                # Shift+Arrow: pan
                elif event.key in (pygame.K_UP, pygame.K_w) and shift:
                    cam[1] -= PAN_SPEED; clamp_camera()
                elif event.key in (pygame.K_DOWN, pygame.K_s) and shift:
                    cam[1] += PAN_SPEED; clamp_camera()
                elif event.key in (pygame.K_LEFT, pygame.K_a) and shift:
                    cam[0] -= PAN_SPEED; clamp_camera()
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and shift:
                    cam[0] += PAN_SPEED; clamp_camera()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                mmb_dragging = True
                mmb_last = event.pos
            # Touchpad/scroll wheel (legacy buttons)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5, 6, 7):
                if event.button == 4:   # wheel up
                    cam[1] -= PAN_SPEED
                elif event.button == 5: # wheel down
                    cam[1] += PAN_SPEED
                elif event.button == 6: # wheel left
                    cam[0] -= PAN_SPEED
                elif event.button == 7: # wheel right
                    cam[0] += PAN_SPEED
                clamp_camera()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                mmb_dragging = False
            # Touchpad/scroll wheel (pygame 2+)
            elif event.type == pygame.MOUSEWHEEL:
                cam[0] -= event.x * PAN_SPEED
                cam[1] -= event.y * PAN_SPEED
                clamp_camera()
            elif event.type == pygame.MOUSEMOTION and mmb_dragging:
                dx = event.pos[0] - mmb_last[0]
                dy = event.pos[1] - mmb_last[1]
                cam[0] -= dx
                cam[1] -= dy
                clamp_camera()
                mmb_last = event.pos

        screen.fill(BG_COLOR)

        # divider bands
        for z in range(1, floors):
            band_y = floor_top_y_world(z) - DIVIDER_H - int(cam[1])
            band_x = PADDING_X - int(cam[0])
            band_rect = pygame.Rect(band_x, band_y, cols * cell_size, DIVIDER_H)
            if band_rect.bottom < 0 or band_rect.top > VIEWPORT_H:
                continue
            pygame.draw.rect(screen, DIVIDER_COLOR, band_rect)
            lbl = font_label.render(
                f"Floor {z - 1}  ^          /          v  Floor {z}",
                True, DIVIDER_TEXT,
            )
            screen.blit(lbl, lbl.get_rect(center=band_rect.center))

        for mc in desc.cells:
            x, y, z = mc.coords
            rect = cell_rect(x, y, z)

            if rect.right < 0 or rect.left > VIEWPORT_W:
                continue
            if rect.bottom < 0 or rect.top > VIEWPORT_H:
                continue

            if mc.kind == "start":
                pygame.draw.rect(screen, START_COLOR, rect)
                lbl = font_cell.render("S", True, TEXT_COLOR)
                screen.blit(lbl, lbl.get_rect(center=rect.center))
            elif mc.kind == "finish":
                pygame.draw.rect(screen, FINISH_COLOR, rect)
                lbl = font_cell.render("F", True, TEXT_COLOR)
                screen.blit(lbl, lbl.get_rect(center=rect.center))

            has_up   = not mc.walls[ABOVE3]
            has_down = not mc.walls[BELOW3]
            if has_up:
                draw_stair_triangle(screen, rect, "up",   STAIR_UP_CLR)
            if has_down:
                draw_stair_triangle(screen, rect, "down", STAIR_DN_CLR)

            x0, y0 = rect.left,  rect.top
            x1, y1 = rect.right, rect.bottom
            if mc.walls[UP3]:
                pygame.draw.line(screen, WALL_COLOR, (x0, y0), (x1, y0), WALL_WIDTH)
            if mc.walls[DOWN3]:
                pygame.draw.line(screen, WALL_COLOR, (x0, y1), (x1, y1), WALL_WIDTH)
            if mc.walls[LEFT3]:
                pygame.draw.line(screen, WALL_COLOR, (x0, y0), (x0, y1), WALL_WIDTH)
            if mc.walls[RIGHT3]:
                pygame.draw.line(screen, WALL_COLOR, (x1, y0), (x1, y1), WALL_WIDTH)

        # Draw player only on their current floor
        px, py, pz = player
        prect = cell_rect(px, py, pz)
        radius = cell_size // 3
        pygame.draw.circle(screen, PLAYER_BORDER, prect.center, radius + 2)
        pygame.draw.circle(screen, PLAYER_COLOR,  prect.center, radius)

        # Floor indicator
        floor_lbl = font_hud.render(f"Floor: {pz}", True, (60, 60, 120))
        screen.blit(floor_lbl, (VIEWPORT_W - floor_lbl.get_width() - 10, 6))

        # Win overlay
        if won and win_timer > 0:
            win_timer -= 1
            overlay = pygame.Surface((VIEWPORT_W, VIEWPORT_H), pygame.SRCALPHA)
            alpha = min(180, win_timer * 3)
            overlay.fill((255, 215, 0, alpha))
            screen.blit(overlay, (0, 0))
            font_win = pygame.font.SysFont(None, cell_size)
            msg = font_win.render("You reached the finish!", True, (80, 40, 0))
            screen.blit(msg, msg.get_rect(center=(VIEWPORT_W // 2, VIEWPORT_H // 2)))

        # HUD
        hud = font_hud.render(
            "Arrow/WASD: move    Q/E: down/up floor    Scroll/Shift+Arrow/MMB: pan",
            True, (100, 100, 100),
        )
        screen.blit(hud, (8, VIEWPORT_H - 22))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def main(maze_type: str, maze_file: str) -> None:
    """Read a maze from *maze_file* and render it in a pygame window."""
    if maze_type == "2d":
        maze_tree = build_maze_tree_2d_from_file(maze_file)
        print(render_ascii(maze_tree))
        render_pygame2d(maze_tree)
    elif maze_type == "3d":
        maze_tree = build_maze_tree_3d_from_file(maze_file)
        render_pygame3d(maze_tree)
    else:
        raise ValueError("Unsupported maze type. Use '2d' or '3d'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("USAGE: python visualizer.py <maze_type: '2d' | '3d'> <maze_file>", file=sys.stderr)
        raise SystemExit(1)
    main(*sys.argv[1:])