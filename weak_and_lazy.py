"""

"""

import weakref

class weak_and_lazy_ref_data(object):
    """
    Picklable instance data class

    weakref.ref is not picklable.
    """
    def __getstate__(self):
        if hasattr(self, 'arg'):
            return (self.arg,)
        else:
            return ()

    def __setstate__(self, state):
        if len(state) == 0:
            del self.arg
        else:
            self.arg, = state


class weak_and_lazy(object):
    """

    >>> class Level(object):
    ...     def __init__(self, id):
    ...         print("Loaded level: %s" % id)
    ...         self.id = id
    ...         self.next_level = self.id + 1
    ...
    ...     @weak_and_lazy
    ...     def next_level(self, id):
    ...         return Level(id)

    >>> first = Level(1)
    Loaded level: 1
    >>> second = first.next_level
    Loaded level: 2

    >>> second_weak = weakref.ref(second)
    >>> assert second_weak() is not None
    >>> second = None
    >>> assert second_weak() is None

    >>> second = first.next_level
    Loaded level: 2

    >>> second_copy = first.next_level
    >>> assert second_copy is second


    """

    def __init__(self, loader):
        """
        """
        # Copy docstring from loader
        self.__doc__ = loader.__doc__
        # Use its name as key
        self.__key = ' ' + loader.__name__
        # Used to enforce call signature even when no slot is
        # connected.  Can also execute code (called before
        # handlers)
        self.__loader = loader

    def __data(self, instance):
        try:
            # Try to return the dictionary entry corresponding to
            # the key.
            return instance.__dict__[self.__key]
        except KeyError:
            # On the first try this raises a KeyError, The error is
            # caught to write the new entry into the instance
            # dictionary.  The new entry is an instance of
            # boundref, which exhibits the event behaviour.
            data = weak_and_lazy_ref_data()
            instance.__dict__[self.__key] = data
            return data

    def __set__(self, instance, value):
        """
        """
        data = self.__data(instance)
        data.arg = value

    def __get__(self, instance, owner):
        """
        """
        data = self.__data(instance)
        try:
            ref = data.ref()
        except AttributeError:
            ref = None

        if ref is None:
            if hasattr(data, 'arg'):
                ref = self.__loader(instance, data.arg)
            else:
                ref = self.__loader(instance)
            data.ref = weakref.ref(ref)
        return ref


# Execute the doctests if run from the command line.
# Verbose tests: python event.py -v
if __name__ == "__main__":
    import doctest
    doctest.testmod()
