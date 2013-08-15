## weak-and-lazy

Decorator class for weak and lazy references.

- [Description](#description)
- [Why use it?](#why-use-it)
- [Usage example](#usage-example)
- [Gotcha](#gotcha)

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

```python
class Level(object):
    def __init__(self, id, prev=None, next=None):
        print("Loaded level: %s" % id)
        self.id = id
        self.prev_level = ref(prev, self.id - 1)
        self.next_level = ref(next, self.id + 1)

    @weak_and_lazy
    def next_level(self, id):
        '''The next level!'''
        return Level(id, prev=self)

    # alternative syntax:
    prev_level = weak_and_lazy(lambda self,id: Level(id, next=self))
```

Besides the  tremendous memory requirements of  any individual level
it is impossible to load 'all' levels, since these are fundamentally
infinite in number.

So let's load some levels:

```python
>>> first = Level(1)
Loaded level: 1
>>> second = first.next_level
Loaded level: 2
>>> third = second.next_level
Loaded level: 3
>>> second2 = third.prev_level
```

Hey, it works! Notice that the second level is loaded only once? Can
it be garbage collected even if the first and third stay alive?

```python
second_weak = weakref.ref(second)
assert second_weak() is not None
second = second2 = None
assert second_weak() is None
```

Reload it into memory. As you can see, as long as `second` is in use
it will not be loaded again.

```python
>>> second = first.next_level
Loaded level: 2
>>> second_copy = first.next_level
>>> assert second_copy is second
```

What about that sexy docstring of yours?

```python
assert Level.next_level.__doc__ == '''The next level!'''
```

### Gotcha

Let's go even further!

```python
>>> third.prev_level is second
Loaded level: 2
False
>>> second.next_level is third
Loaded level: 3
False
```

Oups! One  step too far... Be  careful, this is something  that your
loader must to take care of.  You can customly assign the references
in order to connect your object graph:

```python
third.prev_level = weakref.ref(second)
second.next_level = weakref.ref(third)
assert third.prev_level is second and second.next_level is third
```
