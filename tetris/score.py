from pathlib import Path


SCORE_FILE = Path(__file__).resolve().parent.parent / 'data' / 'scores.txt'


def update_score(nscore):
    score = max_score()

    SCORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SCORE_FILE.open('w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))

def max_score():
    try:
        with SCORE_FILE.open('r') as f:
            return f.readline().strip() or '0'
    except FileNotFoundError:
        return '0'
