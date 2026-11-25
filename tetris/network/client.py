import queue
import select
import socket
import threading

from tetris.network.protocol import Decoder, encode


class Client:
    def __init__(self, ip, port, name='Jogador'):
        self.events = queue.Queue()
        self.outgoing = queue.Queue(maxsize=128)
        # A primeira mensagem identifica o jogador na sala.
        self.outgoing.put({'type': 'hello', 'name': name})
        self.stopped = threading.Event()
        self.socket = None
        self.thread = threading.Thread(target=self._run, args=(ip, port), daemon=True)
        self.thread.start()

    def send(self, message):
        try:
            self.outgoing.put_nowait(message)
        except queue.Full:
            self.events.put({'type': 'error', 'message': 'A conexão está lenta. Tente novamente.'})
            self.stopped.set()

    def poll(self):
        messages = []
        while True:
            try:
                messages.append(self.events.get_nowait())
            except queue.Empty:
                return messages

    def _run(self, ip, port):
        try:
            with socket.create_connection((ip, port), timeout=3) as connection:
                self.socket = connection
                connection.settimeout(2)
                decoder = Decoder()
                while not self.stopped.is_set():
                    while not self.outgoing.empty():
                        connection.sendall(encode(self.outgoing.get_nowait()))
                    ready, _, _ = select.select([connection], [], [], 0.05)
                    if ready:
                        data = connection.recv(4096)
                        if not data:
                            self.events.put({'type': 'disconnected'})
                            return
                        for message in decoder.feed(data):
                            self.events.put(message)
        except (OSError, ValueError, UnicodeError):
            if not self.stopped.is_set():
                self.events.put({'type': 'error', 'message': 'Não foi possível manter a conexão com o host.'})

    def close(self):
        self.stopped.set()
        if self.socket is not None:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        self.thread.join(timeout=3.5)
