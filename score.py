def update_score(nscore):
    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))

def max_score():
    try:
        with open('scores.txt', 'r') as f:
            return f.readline().strip() or '0'
    except FileNotFoundError:
        return '0'

