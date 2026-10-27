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
- **Multijogador** abre as opções **Criar partida** e **Entrar na partida**, ainda desativadas enquanto a comunicação em rede não está implementada.
- Seta esquerda/direita: mover a peça.
- Seta para cima: girar a peça.
- Seta para baixo: acelerar a queda.

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

O compartilhamento atual funciona no mesmo processo, em execução sequencial. A distribuição da sequência por rede será implementada junto com a comunicação e a concorrência.

## Testes

Na pasta do projeto, com o ambiente virtual ativo:

```bash
python -m unittest discover -s tests -v
```
