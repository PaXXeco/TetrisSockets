# TetrisSockets

O código do jogo foi adaptado da implementação da [Tech With Tim](www.techwithtim.net/tutorials/game-development-with-python/tetris-pygame/).

## Como executar

Com Python instalado, abra um terminal na pasta do projeto:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

- Linux/macOS: `source .venv/bin/activate`
- Windows (PowerShell): `.venv\Scripts\Activate.ps1`

Instale a dependência e inicie o jogo:

```bash
python -m pip install -r requirements.txt
python main.py
```

## Controles

- Clique em **Jogar** e depois em **Um jogador** para começar.
- **Multijogador** abre **Criar partida**, que cria a sala e mostra os IPs locais do computador e a porta para compartilhar, e **Entrar na partida**, com um campo para digitar o IPv4 do host. Nas duas telas cada jogador informa o nome (até 12 caracteres) que aparece para os outros; o último nome usado fica salvo em `data/settings.json`.
- **Configurações** permite salvar a porta de rede (padrão: `10000`, intervalo: `1` a `65535`) em `data/settings.json`. Clique em **Salvar** ou pressione Enter; **Voltar** ou Esc descarta alterações não salvas.
- Seta esquerda/direita: mover a peça.
- Seta para cima: girar a peça.
- Seta para baixo: acelerar a queda.
- Barra de espaço: Hard Drop (leva a peça até a última posição válida e a trava).
- C ou Shift esquerdo: Hold (guarda a peça atual e traz a guardada; na primeira vez, traz a próxima da fila). Só pode ser usado uma vez por peça: o painel **Guardada**, à esquerda, fica apagado até a peça em jogo travar.

Cada linha limpa vale 10 pontos. O nível sobe a cada 100 pontos e deixa a queda 15% mais rápida, de 0,27 s por linha no nível 1 até o limite de 0,05 s (nível 12). O nível aparece no painel à esquerda.

A barra lateral direita mostra as próximas cinco peças, de cima para baixo, na ordem em que entrarão no tabuleiro.

A melhor pontuação fica salva em `data/scores.txt`. O caminho do recorde é resolvido a partir do projeto, independentemente da pasta de onde o jogo é executado.

## Estrutura do projeto

| Arquivo       | Responsabilidade                                                             |
| ------------- | ---------------------------------------------------------------------------- |
| `main.py`   | Ponto de entrada: inicializa o Pygame, cria a janela e abre o menu.          |
| `tetris/core/state.py` | `GameState`: estado da partida e suas ações. |
| `tetris/core/board.py` | Criação do grid, colisões e remoção de linhas. |
| `tetris/core/piece.py` | Peças e conversão para posições. |
| `tetris/core/sequence.py` | Sequência compartilhada com sacolas de sete peças. |
| `tetris/core/shapes.py` | Formatos e cores das sete peças. |
| `tetris/network/server.py` | Servidor da sala: jogadores, semente, ataques, eliminações e classificação. |
| `tetris/network/client.py` | Conexão do jogador com o servidor, em thread própria. |
| `tetris/network/protocol.py` | Formato das mensagens e limites (jogadores por sala, tamanho do nome). |
| `tetris/ui/menu.py` | Menu inicial e escolha do modo de jogo. |
| `tetris/ui/multiplayer.py` | Telas de criar/entrar na partida e a sala de espera. |
| `tetris/ui/settings.py` | Tela de configuração da porta. |
| `tetris/ui/game.py` | Loop da partida, teclado, tempo de queda e mensagens da rede. |
| `tetris/ui/render.py` | Desenho do tabuleiro, da HUD, dos adversários e da classificação. |
| `tetris/ui/layout.py` | Escala da interface conforme o tamanho da janela. |
| `tetris/score.py` | Leitura e gravação do recorde. |
| `tetris/settings.py` | Leitura e gravação da porta e do nome do jogador. |
| `tetris/config.py` | Dimensões da janela, tabuleiro e blocos. |
| `data/scores.txt` | Recorde salvo entre partidas (criado pelo jogo). |
| `data/settings.json` | Porta e nome salvos entre execuções (criado pelo jogo). |

O pacote `tetris/core` contém as regras sem depender do Pygame. O pacote `tetris/network` cuida da comunicação por sockets TCP. O pacote `tetris/ui` contém a interface e usa essas regras para controlar a partida.

## Sequência de peças

Cada sacola contém os sete tipos de peças em ordem embaralhada. Ao terminar uma sacola, a sequência gera outra. O jogo individual já usa essa sequência.

Para uma partida com vários jogadores, passe a mesma `PieceSequence` para os estados:

```python
from tetris.core.sequence import PieceSequence
from tetris.core.state import GameState

sequence = PieceSequence()
player_one = GameState(sequence)
player_two = GameState(sequence)
```

Cada jogador recebe a mesma ordem, com consumo independente e objetos de peças próprios. A sequência guarda os tipos gerados para permitir que jogadores mais lentos os consultem depois. Uma semente opcional, como `PieceSequence(seed=42)`, permite reproduzir a ordem.

O exemplo acima compartilha a sequência no mesmo processo. Nas partidas em rede, cada cliente cria sua sequência usando a semente enviada pelo servidor.

## Partida em rede

1. Em todos os computadores, use a mesma porta em **Configurações** (padrão: `10000`).
2. No computador host, abra **Jogar → Multijogador → Criar partida**, informe seu nome e clique em **Criar sala**.
3. Nos outros computadores, abra **Entrar na partida**, informe o nome e o IPv4 do host e clique em **Conectar**.
4. A sala lista quem já entrou (de 2 a 10 jogadores). Quando todos estiverem na lista, o host clica em **Iniciar partida**.

Para testar em um só computador, abra o jogo mais de uma vez e conecte os outros em `127.0.0.1`.

O host também participa como cliente do servidor, que aceita conexões TCP nas interfaces locais (`0.0.0.0`). Os computadores devem estar na mesma rede e o firewall do host deve permitir a conexão na porta escolhida. Depois que a partida começa, a sala não aceita novos jogadores. Nomes repetidos recebem um sufixo, como `Ana (2)`.

Durante a partida, a janela ganha uma coluna à direita com o tabuleiro, o nome e a pontuação de cada adversário; a coluna fica mais larga a partir de cinco adversários. O servidor distribui a mesma semente a todos, encaminha as prévias dos tabuleiros e os ataques e comunica o resultado. Limpar duas, três ou quatro linhas envia, respectivamente, uma, duas ou quatro linhas cinzas com um buraco aleatório a um adversário sorteado entre os que ainda estão jogando.

Quem perde é eliminado e assiste ao restante; quem sai ou desconecta também conta como eliminado. A partida termina quando sobra um jogador, e todos veem a classificação: o vencedor em primeiro e os demais do último ao primeiro eliminado, com a pontuação de cada um. Enter ou Esc volta ao menu. Se o host sair, a partida é encerrada para todos.

As mensagens são JSON separados por quebra de linha. A comunicação roda em threads com filas para manter a interface responsiva. As regras de movimento e pontuação são calculadas pelos clientes.
