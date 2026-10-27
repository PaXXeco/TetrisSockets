import random

from tetris.core.shapes import shapes


class PieceSequence:
    """Sequência da partida; cada iterador começa na primeira peça.

    Guarda apenas os tipos, nunca os objetos mutáveis de cada jogador.
    """

    def __init__(self, seed=None):
        self._random = random.Random(seed)
        self._types = []

    def __iter__(self):
        index = 0
        while True:
            if index == len(self._types):
                bag = list(range(len(shapes)))
                self._random.shuffle(bag)
                self._types.extend(bag)
            yield self._types[index]
            index += 1
