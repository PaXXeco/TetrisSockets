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
- **Multijogador** abre **Criar partida**, que mostra os IPs locais do computador e a porta para compartilhar com o outro jogador, e **Entrar na partida**, com um campo para digitar o IPv4 do host. Use o endereço da rede compartilhada pelos dois computadores.
- **Configurações** permite salvar a porta de rede (padrão: `10000`, intervalo: `1` a `65535`) em `data/settings.json`. Clique em **Salvar** ou pressione Enter; **Voltar** ou Esc descarta alterações não salvas.
- Seta esquerda/direita: mover a peça.
- Seta para cima: girar a peça.
- Seta para baixo: acelerar a queda.
- Barra de espaço: Hard Drop (leva a peça até a última posição válida e a trava).

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
| `tetris/ui/menu.py` | Menu inicial com o botão **Jogar**. |
| `tetris/ui/game.py` | Loop da partida, teclado e tempo de queda. |
| `tetris/ui/render.py` | Desenho do tabuleiro e da HUD. |
| `tetris/score.py` | Leitura e gravação do recorde. |
| `tetris/config.py` | Dimensões da janela, tabuleiro e blocos. |
| `data/scores.txt` | Recorde salvo entre partidas. |
| `tests/` | Testes automatizados. |

O pacote `tetris/core` contém as regras sem depender do Pygame. O pacote `tetris/ui` contém a interface e usa essas regras para controlar a partida.

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

Cada jogador recebe a mesma ordem, com consumo independente e objetos de peças próprios. A sequência guarda os tipos gerados para permitir que jogadores mais lentos os consultem depois. Uma semente opcional, como `PieceSequence(seed=42)`, permite reproduzir a ordem nos testes.

O exemplo acima compartilha a sequência no mesmo processo. Nas partidas em rede, cada cliente cria sua sequência usando a semente enviada pelo servidor.

## Partida em rede

1. Nos dois computadores, use a mesma porta em **Configurações** (padrão: `10000`).
2. No computador host, abra **Jogar → Multijogador → Criar partida** e clique em **Hospedar**.
3. No outro computador, abra **Entrar na partida**, digite o IPv4 do host e clique em **Conectar**.

A partida começa quando os dois clientes estão conectados. O host também participa como cliente do servidor, que aceita conexões TCP nas interfaces locais (`0.0.0.0`). Os computadores devem estar na mesma rede e o firewall do host deve permitir a conexão na porta escolhida.

O servidor distribui a mesma semente aos dois jogadores, encaminha as prévias dos tabuleiros e os ataques e comunica o resultado aos dois clientes. Limpar duas, três ou quatro linhas envia, respectivamente, uma, duas ou quatro linhas cinzas com um buraco aleatório ao adversário. Esc sai da partida; uma desconexão encerra a sessão do outro jogador.

As mensagens são JSON separados por quebra de linha. A comunicação roda em threads com filas para manter a interface responsiva. As regras de movimento e pontuação são calculadas pelos clientes.

## Testes

Na pasta do projeto, com o ambiente virtual ativo:

```bash
python -m unittest discover -s tests -v
```
