from tetris.config import rows, columns
from tetris.core.piece import convert_shape_format

def create_grid(locked_positions=None):
    if locked_positions is None:
        locked_positions = {}
    grid = [[(0,0,0) for x in range(columns)] for x in range(rows)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_positions:
                c = locked_positions[(j,i)]
                grid[i][j] = c
    return grid

def valid_space(shape, grid):
    for x, y in convert_shape_format(shape):
        if x < 0 or x >= columns or y >= rows:
            return False
        if y > -1 and grid[y][x] != (0,0,0):
            return False

    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def clear_rows(grid, locked):
    cleared = {y for y, row in enumerate(grid) if (0, 0, 0) not in row}
    if not cleared:
        return 0

    # Cada bloco desce uma posição por linha removida abaixo dele.
    remaining = {}
    for (x, y), color in locked.items():
        if y not in cleared:
            drop = sum(cleared_y > y for cleared_y in cleared)
            remaining[(x, y + drop)] = color
    locked.clear()
    locked.update(remaining)
    return len(cleared)
