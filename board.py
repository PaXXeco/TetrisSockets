from config import rows, columns
from piece import convert_shape_format

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
    inc = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            # add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc
