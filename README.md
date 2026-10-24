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

- Clique em **Jogar** para começar.
- Seta esquerda/direita: mover a peça.
- Seta para cima: girar a peça.
- Seta para baixo: acelerar a queda.

A melhor pontuação fica salva em `scores.txt`. Execute o jogo a partir da pasta do projeto.

## Estrutura do projeto

| Arquivo       | Responsabilidade                                                             |
| ------------- | ---------------------------------------------------------------------------- |
| `main.py`   | Ponto de entrada: inicializa o Pygame, cria a janela e abre o menu.          |
| `menu.py`   | Menu inicial com o botão **Jogar**.                                   |
| `game.py`   | Loop da partida: tempo de queda, teclado e desenho a cada frame.             |
| `state.py`  | `GameState`: estado da partida (grid, peças, pontuação) e suas ações. |
| `board.py`  | Regras do tabuleiro: criar o grid, validar posições, limpar linhas.        |
| `piece.py`  | Classe `Piece`, sorteio da próxima peça e conversão para posições.    |
| `shapes.py` | Formatos e cores das sete peças (S, Z, I, O, J, L, T).                      |
| `render.py` | Funções de desenho: tabuleiro, próxima peça, pontuação e textos.       |
| `score.py`  | Leitura e gravação da melhor pontuação em `scores.txt`.                |
| `config.py` | Constantes: tamanho da janela, linhas, colunas e tamanho do bloco.           |
