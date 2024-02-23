def unseen_before(xs):
    seen = set()
    return [x for x in xs if not (x in seen or seen.add(x))]

assert unseen_before([1, 2, 2, 1, 0]) == [1, 2, 0]