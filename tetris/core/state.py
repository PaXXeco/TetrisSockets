from collections import deque

from tetris.core.board import create_grid, valid_space, check_lost, clear_rows
from tetris.core.piece import Piece, convert_shape_format
from tetris.core.sequence import PieceSequence
from tetris.core.shapes import shapes

# Estado de uma partida, sem depender do pygame
class GameState(object):
    def __init__(self, sequence=None):
        # Compartilhe a sequência entre jogadores, mantendo um iterador por estado.
        self._piece_types = iter(sequence if sequence is not None else PieceSequence())
        self.score = 0
        self.locked_positions = {}  # (x,y):(255,0,0)
        self.grid = create_grid(self.locked_positions)
        self.current_piece = self._new_piece()
        self.next_pieces = deque(self._new_piece() for _ in range(5))
        self.change_piece = False

    @property
    def next_piece(self):
        return self.next_pieces[0]

    def _new_piece(self):
        return Piece(5, 0, shapes[next(self._piece_types)])

    def refresh_grid(self):
        self.grid = create_grid(self.locked_positions)

    def move(self, dx, dy):
        self.current_piece.x += dx
        self.current_piece.y += dy
        if not valid_space(self.current_piece, self.grid):
            self.current_piece.x -= dx
            self.current_piece.y -= dy

    def rotate(self):
        piece = self.current_piece
        piece.rotation = (piece.rotation + 1) % len(piece.shape)
        if not valid_space(piece, self.grid):
            piece.rotation = (piece.rotation - 1) % len(piece.shape)

    # Queda automática: se a peça não pode descer, ela é travada no próximo update
    def fall(self):
        self.current_piece.y += 1
        if not valid_space(self.current_piece, self.grid) and self.current_piece.y > 0:
            self.current_piece.y -= 1
            self.change_piece = True

    # Desenha a peça atual no grid e, se ela travou, troca de peça e limpa as linhas
    def update(self):
        shape_pos = convert_shape_format(self.current_piece)

        for x, y in shape_pos:
            if y > -1:
                self.grid[y][x] = self.current_piece.color

        if self.change_piece:
            for pos in shape_pos:
                self.locked_positions[pos] = self.current_piece.color
            self.current_piece = self.next_pieces.popleft()
            self.next_pieces.append(self._new_piece())
            self.change_piece = False
            self.score += clear_rows(self.grid, self.locked_positions) * 10

    def lost(self):
        return check_lost(self.locked_positions)
