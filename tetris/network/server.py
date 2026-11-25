import os
import random
import select
import socket
import threading

from tetris.network.protocol import Decoder, encode, valid_board, clean_name, MAX_PLAYERS

FAILURES = (OSError, ValueError, UnicodeError)


class Player:
    def __init__(self, connection):
        self.socket = connection
        self.decoder = Decoder()
        self.name = ''
        self.score = 0
        self.alive = True

    def read(self):
        data = self.socket.recv(4096)
        if not data:
            raise ConnectionError('Jogador desconectado')
        return self.decoder.feed(data)

    def send(self, message):
        """Devolve False se o jogador não puder mais receber mensagens."""
        if self.socket is None:
            return False
        try:
            self.socket.sendall(encode(message))
            return True
        except OSError:
            return False

    def close(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None


class Server:
    """Servidor da sala; o próprio host também entra como cliente.

    Os jogadores entram na sala até o host chamar start_game().
    """

    def __init__(self, port, host='0.0.0.0'):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Sem isso, as conexões da partida anterior seguram a porta por
            # cerca de um minuto (TIME_WAIT) e não dá para hospedar de novo.
            # No Windows a opção deixaria dois hosts abrirem a mesma porta.
            if os.name != 'nt':
                self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listener.bind((host, port))
            self.listener.listen(MAX_PLAYERS)
            self.listener.settimeout(0.2)
        except OSError:
            self.listener.close()
            raise
        self.port = self.listener.getsockname()[1]
        self.stopped = threading.Event()
        self.start_requested = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def start_game(self):
        """Pedido do host; só vale com pelo menos dois jogadores na sala."""
        self.start_requested.set()

    def _run(self):
        players = []
        try:
            if self._lobby(players):
                self.listener.close()
                self._game(players)
        finally:
            for player in players:
                player.close()
            self.listener.close()

    def _unique_name(self, name, players):
        taken = {player.name.casefold() for player in players}
        candidate, number = name, 2
        while candidate.casefold() in taken:
            candidate = f'{name} ({number})'
            number += 1
        return candidate

    def _lobby(self, players):
        while not self.stopped.is_set():
            named = [player for player in players if player.name]
            if self.start_requested.is_set():
                if len(named) >= 2:
                    for player in players:
                        if not player.name:
                            player.close()
                    players[:] = named
                    return True
                self.start_requested.clear()
            ready, _, _ = select.select([self.listener] + [p.socket for p in players], [], [], 0.1)
            changed = False
            for connection in ready:
                if connection is self.listener:
                    try:
                        client, _ = self.listener.accept()
                    except OSError:
                        continue
                    client.settimeout(2)
                    player = Player(client)
                    if len(players) >= MAX_PLAYERS:
                        player.send({'type': 'error', 'message': 'A sala está cheia.'})
                        player.close()
                    else:
                        players.append(player)
                    continue
                player = next(p for p in players if p.socket is connection)
                try:
                    for message in player.read():
                        name = clean_name(message.get('name'))
                        if message.get('type') != 'hello' or player.name or not name:
                            raise ValueError('Mensagem inválida')
                        player.name = self._unique_name(name, players)
                        changed = True
                except FAILURES:
                    changed = changed or bool(player.name)
                    player.close()
                    players.remove(player)
            if changed:
                named = [player for player in players if player.name]
                names = [player.name for player in named]
                for index, player in enumerate(named):
                    player.send({'type': 'lobby', 'players': names, 'you': index})
        return False

    def _game(self, players):
        eliminated = []  # na ordem em que saíram da partida

        def send(player, message):
            if player.socket is not None and not player.send(message):
                drop(player)

        def eliminate(player):
            if player.alive:
                player.alive = False
                eliminated.append(player)
                for other in players:
                    if other is not player:
                        send(other, {'type': 'eliminated', 'player': players.index(player)})

        # Quem desconecta ou manda mensagem inválida sai da partida; os outros continuam.
        def drop(player):
            player.close()
            eliminate(player)

        seed = random.SystemRandom().randrange(2 ** 63)
        names = [player.name for player in players]
        for index, player in enumerate(players):
            send(player, {'type': 'start', 'seed': seed, 'player': index, 'names': names})

        while not self.stopped.is_set():
            alive = [player for player in players if player.alive]
            if len(alive) <= 1:
                # O vencedor vem primeiro; depois, do último ao primeiro eliminado.
                ranking = [{'player': players.index(player), 'name': player.name, 'score': player.score}
                           for player in alive + eliminated[::-1]]
                for player in players:
                    player.send({'type': 'result', 'won': player.alive, 'ranking': ranking})
                return
            ready, _, _ = select.select([p.socket for p in players if p.socket is not None], [], [], 0.1)
            for connection in ready:
                player = next((p for p in players if p.socket is connection), None)
                if player is None:
                    continue
                try:
                    for message in player.read():
                        kind = message.get('type')
                        if kind == 'board' and valid_board(message):
                            player.score = message['score']
                            for other in players:
                                if other is not player:
                                    send(other, {'type': 'board', 'player': players.index(player),
                                                 'grid': message['grid'], 'score': message['score']})
                        elif kind == 'attack' and type(message.get('lines')) is int and message['lines'] in (1, 2, 4):
                            targets = [other for other in players if other.alive and other is not player]
                            if player.alive and targets:
                                holes = [random.randrange(10) for _ in range(message['lines'])]
                                send(random.choice(targets), {'type': 'garbage', 'holes': holes})
                        elif kind == 'game_over':
                            score = message.get('score')
                            if type(score) is int and 0 <= score <= 1000000000:
                                player.score = score
                            eliminate(player)
                        else:
                            raise ValueError('Mensagem inválida')
                except FAILURES:
                    drop(player)

    def close(self):
        self.stopped.set()
        self.thread.join(timeout=3)
        self.listener.close()
