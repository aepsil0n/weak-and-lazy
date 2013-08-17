# encoding=utf-8
"""
Provides a decorator class for weak and lazy references.

### License

Copyright © 2013 Thomas Gläßle <t_glaessle@gmx.de>

This work  is free. You can  redistribute it and/or modify  it under the
terms of the Do What The Fuck  You Want To Public License, Version 2, as
published by Sam Hocevar. See the COPYING file for more details.

This program  is free software.  It comes  without any warranty,  to the
extent permitted by applicable law.


### Overview

List of objects:

 - weak_and_lazy    decorator class for weak and lazy reference attributes
 - ref              data class used to bind instance and loader params

Running this module from the command  line will execute the doctests. To
enable verbose mode, run:

    python event.py -v

"""

import weakref
import functools


class ref(object):
    """
    Data class for a @weak_and_lazy reference instance.

    This class is Used to bind a reference and loader parameters to your
    lazy reference. It is  implemented as a class and not  as a tuple or
    dictionary for mainly one reason:

     - weakref.ref is not picklable and we do not want to pickle it!
     - the syntax to access object attributes is nicer than tuple or
       dictionary elements

    I know these were at least four reasons, but only the second one was
    really important. (JK)

    The following methods are overloaded:

     - `__init__` initialize from optional hard-reference and argument list
     - `__getstate__` and `__setstate__` to define how pickling works

    Due  to the  use of  `__slots__` instances  of this  class are  very
    restricted. See also:

    http://docs.python.org/3.3/reference/datamodel.html?highlight=__slots__#object.__slots__

    Defined instance attributes:

     - `ref`                weak reference to loaded object
     - `args`, `kwargs`     parameters for object loader

    The class  is defined  in global  scope because this  seems to  be a
    requirement for picklable classes.


    NOTE: some  builtins are not  weak-refable and can therefore  not be
    used with this class:

    >>> ref(dict()) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TypeError: cannot create weak reference to 'dict' object

    For such cases you could use trivial inheritances:

    >>> class Dict(dict):
    ...     pass

    NOTE: `ref` expects  a hard reference in its  constructor but stores
    only a weak reference:

    >>> d = Dict(Foo="Bar")
    >>> r = ref(d)
    >>> assert r.ref() is not None
    >>> del d
    >>> assert r.ref() is None

    Objects of this class are picklable:

    >>> import pickle
    >>> r = ref(Dict(Foo="Bar"), 1, 2, 3, Bar="Foo")
    >>> p = pickle.loads(pickle.dumps(r))
    >>> assert p.args == r.args and p.kwargs == r.kwargs

    """
    __slots__ = ['ref', 'args', 'kwargs']

    def __init__(self, ref=None, *args, **kwargs):
        """
        Initialize with empty parameter list.

        Note `ref`  is expected to be  a hard reference but  only a weak
        reference will be stored.

        """
        if ref is not None:
            self.ref = weakref.ref(ref)
        self.args = args
        self.kwargs = kwargs

    def __getstate__(self):
        """Pickle the loader parameters."""
        return self.args, self.kwargs

    def __setstate__(self, state):
        """Unpickle the loader parameters."""
        self.args, self.kwargs = state


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
    ...     def __init__(self, id, prev=None, next=None):
    ...         print("Loaded level: %s" % id)
    ...         self.id = id
    ...         self.prev_level = ref(prev, self.id - 1)
    ...         self.next_level = ref(next, self.id + 1)
    ...
    ...     @weak_and_lazy
    ...     def next_level(self, id):
    ...         '''The next level!'''
    ...         return Level(id, prev=self)
    ...
    ...     # alternative syntax:
    ...     prev_level = weak_and_lazy(lambda self,id: Level(id, next=self))

    Besides the  tremendous memory requirements of  any individual level
    it is impossible to load 'all' levels, since these are fundamentally
    infinite in number.

    So let's load some levels:

    >>> first = Level(1)
    Loaded level: 1
    >>> second = first.next_level
    Loaded level: 2
    >>> third = second.next_level
    Loaded level: 3
    >>> assert third.prev_level is second

    Hey, it works! Notice that the second level is loaded only once? Can
    it be garbage collected even if the first and third stay alive?

    >>> second_weak = weakref.ref(second)
    >>> assert second_weak() is not None
    >>> second = None
    >>> assert second_weak() is None

    Reload it into memory. As you can see, as long as `second` is in use
    it will not be loaded again.

    >>> second = first.next_level
    Loaded level: 2
    >>> assert first.next_level is second

    What about that sexy docstring of yours?

    >>> assert Level.next_level.__doc__ == '''The next level!'''

    ### Gotcha

    Let's go even further!

    >>> third.prev_level is second
    Loaded level: 2
    False
    >>> second.next_level is third
    Loaded level: 3
    False

    Oups! One  step too far... Be  careful, this is something  that your
    loader must to take care of.  You can customly assign the references
    in order to connect your object graph:

    >>> third.prev_level = weakref.ref(second)
    >>> second.next_level = weakref.ref(third)
    >>> assert third.prev_level is second and second.next_level is third

    """

    def __init__(self, loader):
        """Initialize the attribute with a loader function."""
        functools.update_wrapper(self, loader)
        # Use its name as key
        self.key = ' ' + loader.__name__
        # Used to enforce call signature even when no slot is
        # connected.  Can also execute code (called before
        # handlers)
        self.loader = loader

    def __data(self, instance):
        """Get the data associated to the specified instance."""
        try:
            # Try to return the dictionary entry corresponding to
            # the key.
            data = instance.__dict__[self.key]
        except KeyError:
            # On the first try this raises a KeyError, The error is
            # caught to write the new entry into the instance
            # dictionary. 
            data = ref()
            instance.__dict__[self.key] = data
        return data

    def __set__(self, instance, value):
        """Set reference and parameters for the loader."""
        if isinstance(value, weakref.ref):
            self.__data(instance).ref = value
        else:
            instance.__dict__[self.key] = value

    def __get__(self, instance, owner):
        """Load and return reference to the desired object."""
        # Allow access via the owner class
        if instance is None:
            return self
        data = self.__data(instance)
        try:
            ref = data.ref()
        except AttributeError:
            ref = None
        if ref is None:
            ref = self.loader(instance, *data.args, **data.kwargs)
            data.ref = weakref.ref(ref)
        return ref


# Execute the doctests if run from the command line.
if __name__ == "__main__":
    import doctest
    doctest.testmod()
