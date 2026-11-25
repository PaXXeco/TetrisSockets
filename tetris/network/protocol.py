import json

MAX_MESSAGE = 32768
MAX_PLAYERS = 10
MAX_NAME = 12


def encode(message):
    return (json.dumps(message, separators=(',', ':')) + '\n').encode('utf-8')


class Decoder:
    """TCP pode dividir ou juntar mensagens; só lemos linhas completas."""

    def __init__(self):
        self.buffer = b''

    def feed(self, data):
        self.buffer += data
        messages = []
        while b'\n' in self.buffer:
            line, self.buffer = self.buffer.split(b'\n', 1)
            if len(line) > MAX_MESSAGE:
                raise ValueError('Mensagem muito grande')
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError('Mensagem inválida')
            messages.append(message)
        if len(self.buffer) > MAX_MESSAGE:
            raise ValueError('Mensagem muito grande')
        return messages


def valid_board(message):
    grid = message.get('grid')
    score = message.get('score')
    return (type(score) is int and 0 <= score <= 1000000000
            and isinstance(grid, list) and len(grid) == 20
            and all(isinstance(row, list) and len(row) == 10
                    and all(isinstance(cell, list) and len(cell) == 3
                            and all(type(c) is int and 0 <= c <= 255 for c in cell)
                            for cell in row) for row in grid))


def clean_name(value):
    """Nome sem espaços sobrando e limitado a MAX_NAME; '' se for inválido."""
    if not isinstance(value, str):
        return ''
    return ' '.join(''.join(c for c in value if c.isprintable()).split())[:MAX_NAME].strip()
