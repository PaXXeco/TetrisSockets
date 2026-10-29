import random
import select
import socket
import threading

from tetris.network.protocol import Decoder, encode, valid_board


class Server:
    """Servidor para dois clientes; o próprio host também entra como cliente."""

    def __init__(self, port, host='0.0.0.0'):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.listener.bind((host, port))
            self.listener.listen(2)
            self.listener.settimeout(0.2)
        except OSError:
            self.listener.close()
            raise
        self.port = self.listener.getsockname()[1]
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _send(self, client, message):
        client.sendall(encode(message))

    def _run(self):
        clients = []
        try:
            while len(clients) < 2 and not self.stopped.is_set():
                try:
                    client, _ = self.listener.accept()
                except socket.timeout:
                    continue
                client.settimeout(2)
                clients.append(client)
                self._send(client, {'type': 'waiting'})
            if self.stopped.is_set():
                return
            self.listener.close()
            seed = random.SystemRandom().randrange(2 ** 63)
            for player, client in enumerate(clients):
                self._send(client, {'type': 'start', 'seed': seed, 'player': player})
            decoders = {client: Decoder() for client in clients}
            while not self.stopped.is_set():
                ready, _, _ = select.select(clients, [], [], 0.1)
                for client in ready:
                    opponent = clients[1 - clients.index(client)]
                    data = client.recv(4096)
                    if not data:
                        self._send(opponent, {'type': 'disconnected'})
                        return
                    for message in decoders[client].feed(data):
                        kind = message.get('type')
                        if kind == 'game_over':
                            for receiver in clients:
                                self._send(receiver, {'type': 'result', 'won': receiver is opponent})
                            return
                        if kind == 'attack' and type(message.get('lines')) is int and message['lines'] in (1, 2, 4):
                            holes = [random.randrange(10) for _ in range(message['lines'])]
                            self._send(opponent, {'type': 'garbage', 'holes': holes})
                        elif kind == 'board' and valid_board(message):
                            self._send(opponent, message)
                        else:
                            raise ValueError('Mensagem inválida')
        except (OSError, ValueError, UnicodeError):
            for client in clients:
                try:
                    self._send(client, {'type': 'disconnected'})
                except OSError:
                    pass
        finally:
            for client in clients:
                client.close()
            self.listener.close()

    def close(self):
        self.stopped.set()
        self.listener.close()
        self.thread.join(timeout=3)
