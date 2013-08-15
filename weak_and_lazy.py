"""
Provides a decorator class for weak and lazy references.

Provides the `weak_and_lazy` decorator class.

Running this module from the command  line will execute the doctests. To
enable verbose mode, run:

    python event.py -v

"""

import weakref


class _weak_and_lazy_ref_data(object):
    """
    Internal data class for a @weak_and_lazy reference instance.

    This class is used only internally and as a user you probably do not
    need to care much about it. It  is implemented as a class and not as
    a tuple or dictionary for mainly one reason:

     - weakref.ref is not picklable and we do not want to pickle it!
     - the syntax to access object attributes is nicer than tuple or
       dictionary elements

    I know these were at least four reasons, but only the second one was
    really important.

    The following methods are overloaded:

     - `__init__` to create an empty initial paramater set
     - `__getstate__` and `__setstate__` to define how pickling works
     - `__call__` just for convenince to define the loader parameters

    The class  is defined  in global  scope because this  seems to  be a
    requirement for picklable classes.

    """
    def __init__(self):
        """
        Initialize with empty parameter list.

        There is also an attribute called `ref` but this is only created
        if and when needed.

        """
        self.args = list()
        self.kwargs = dict()

    def __getstate__(self):
        """Pickle the loader parameters."""
        return self.args, self.kwargs

    def __setstate__(self, state):
        """Unpickle the loader parameters."""
        self.args, self.kwargs = state

    def __call__(self, *args, **kwargs):
        """Set the loader parameters."""
        self.args = args
        self.kwargs = kwargs



class weak_and_lazy(object):
    """
    Decorator class for weak and lazy references.

    ### Description

    Decorator  class for  a  property  that looks  like  a reference  to
    outsiders but is  in fact a dynamic object-loader.  After loading it
    stores a weak reference to the  object so it can be remembered until
    it gets destroyed.

    This means that the referenced object

     - will be loaded only **if** and **when** it is needed
     - can be garbage collected when it is not in use anymore 


    ### Why use it?

    You probably do not need it, if you are asking this.

    Still, for what in the world might that be useful?

    Suppose you program a video game  with several levels. As the levels
    have very intense  memory requirements, you want to  load only those
    into memory which you actually need at the moment. If a level is not
    needed anymore (every player left  the level), the garbage collector
    should be able to tear it into the abyss. And while fulfilling these
    requirements  the interface  should still  feel like  you are  using
    normal references. *That* is for what you can use *weak-and-lazy*.


    ### Usage example

    Define a `Level` class with VERY intense memory requirements:

    >>> class Level(object):
    ...     def __init__(self, id):
    ...         print("Loaded level: %s" % id)
    ...         self.id = id
    ...         self.next_level = self.id + 1
    ...
    ...     @weak_and_lazy
    ...     def next_level(self, id):
    ...         return Level(id)

    Besides the  tremendous memory requirements of  any individual level
    it is impossible to load 'all' levels, since these are fundamentally
    infinite in number.

    So let's load the first two levels:

    >>> first = Level(1)
    Loaded level: 1
    >>> second = first.next_level
    Loaded level: 2

    Hey, it works! Can the second level be garbage collected even if the
    first one stays alive?

    >>> second_weak = weakref.ref(second)
    >>> assert second_weak() is not None
    >>> second = None
    >>> assert second_weak() is None

    Reload it into memory. As you can see, as long as `second` is in use
    it will not be loaded again.

    >>> second = first.next_level
    Loaded level: 2
    >>> second_copy = first.next_level
    >>> assert second_copy is second

    """

    def __init__(self, loader):
        """Initialize the attribute with a loader function."""
        # Copy docstring from loader
        self.__doc__ = loader.__doc__
        # Use its name as key
        self.__key = ' ' + loader.__name__
        # Used to enforce call signature even when no slot is
        # connected.  Can also execute code (called before
        # handlers)
        self.__loader = loader

    def __data(self, instance):
        """Get the data associated to the specified instance."""
        try:
            # Try to return the dictionary entry corresponding to
            # the key.
            return instance.__dict__[self.__key]
        except KeyError:
            # On the first try this raises a KeyError, The error is
            # caught to write the new entry into the instance
            # dictionary.  The new entry is an instance of
            # boundref, which exhibits the event behaviour.
            data = _weak_and_lazy_ref_data()
            instance.__dict__[self.__key] = data
            return data

    def __set__(self, instance, value):
        """Bind a parameter for the loader."""
        self.__data(instance)(value)

    def __get__(self, instance, owner):
        """Load and return the desired object."""
        data = self.__data(instance)
        try:
            ref = data.ref()
        except AttributeError:
            ref = None
        if ref is None:
            ref = self.__loader(instance, *data.args, **data.kwargs)
            data.ref = weakref.ref(ref)
        return ref


# Execute the doctests if run from the command line.
if __name__ == "__main__":
    import doctest
    doctest.testmod()
