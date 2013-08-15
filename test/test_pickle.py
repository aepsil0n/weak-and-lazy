
import pickle

from weak_and_lazy import weak_and_lazy


class Level(object):
    def __init__(self, id):
        self.id = id
        self.next_level = self.id + 1

    @weak_and_lazy
    def next_level(self, id):
        return Level(id)


def test_pickle():

    first = Level(1)
    second = first.next_level

    dump = pickle.dumps(first)

    first_copy = pickle.loads(dump)
    assert first.id == first_copy.id

    second_copy = first_copy.next_level
    assert second.id == second_copy.id
