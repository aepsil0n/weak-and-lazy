"""

"""

import weakref

class weak_and_lazy(object):
    """

    >>> class Level(object):
    ...     def __init__(self, id):
    ...         print("Created level: %s" % id)
    ...         self.id = id
    ...         self.next_level = self.id + 1
    ...
    ...     @weak_and_lazy
    ...     def next_level(self, id):
    ...         return Level(id)

    >>> first = Level(1)
    Created level: 1
    >>> second = first.next_level
    Created level: 2

    >>> second_weak = weakref.ref(second)
    >>> assert second_weak() is not None
    >>> second = None
    >>> assert second_weak() is None

    >>> second = first.next_level
    Created level: 2

    >>> second_copy = first.next_level
    >>> assert second_copy is second

    >>

    """

    def __init__(self, function):
        """
        """
        # Copy docstring from function
        self.__doc__ = function.__doc__
        # Use its name as key
        self._key = ' ' + function.__name__
        # Used to enforce call signature even when no slot is
        # connected.  Can also execute code (called before
        # handlers)
        self._function = function

    def __bound(self, instance):
        try:
            # Try to return the dictionary entry corresponding to
            # the key.
            return instance.__dict__[self._key]
        except KeyError:
            # On the first try this raises a KeyError, The error is
            # caught to write the new entry into the instance
            # dictionary.  The new entry is an instance of
            # boundref, which exhibits the event behaviour.
            bound = dict()
            instance.__dict__[self._key] = bound
            return bound

    def __set__(self, instance, value):
        """
        """
        bound = self.__bound(instance)
        bound['arg'] = value

    def __get__(self, instance, owner):
        """
        """
        bound = self.__bound(instance)
        try:
            ref = bound['ref']()
        except KeyError:
            ref = None

        if ref is None:
            if 'arg' in bound:
                ref = self._function(instance, bound['arg'])
            else:
                ref = self._function(instance)
            bound['ref'] = weakref.ref(ref)
        return ref


# Execute the doctests if run from the command line.
# Verbose tests: python event.py -v
if __name__ == "__main__":
    import doctest
    doctest.testmod()
