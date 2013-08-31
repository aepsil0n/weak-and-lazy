'''
This module contains tests of correct handling of `None` references.
'''

from weak_and_lazy import weak_and_lazy, ref


class Stuff(object):

    def __init__(self, content, other_stuff=None):
        self.content = content
        self.other = other_stuff

    @weak_and_lazy
    def other(self, content=None):
        if content is not None:
            return Stuff(content)


def test_none_reference():
    '''None reference handling'''
    stuff = Stuff(13)
    stuff.other = ref(None, 17)
    assert stuff.other.content == 17
    stuff.other = ref(None, None)
    assert stuff.other is None
    stuff.other = None
    assert stuff.other is None
