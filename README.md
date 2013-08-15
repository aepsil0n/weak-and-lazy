## weak-and-lazy

- [Description](#description)
- [Why use it?](#why-use-it)
- [Usage example](#usage-example)

### Description

Decorator class for a property that  looks like a reference to outsiders
but is in  fact a dynamic object-loader. After loading  it stores a weak
reference to the object so it can be remembered until it gets destroyed.

This means that the referenced object

 - will be loaded only **if** and **when** it is needed
 - can be garbage collected when it is not in use anymore 


### Why use it?

You probably do not need it, if you are asking this.

Still, for what in the world might that be useful?

Suppose you program a video game with several levels. As the levels have
very  intense memory  requirements, you  want  to load  only those  into
memory which you actually  need at the moment. If a  level is not needed
anymore (every player  left the level), the garbage  collector should be
able to tear it into the  abyss. And while fulfilling these requirements
the interface  should still feel  like you are using  normal references.
*That* is for what you can use *weak-and-lazy*.


### Usage example

Define a `Level` class with VERY intense memory requirements:

```python
class Level(object):
    def __init__(self, id):
        print("Loaded level: %s" % id)
        self.id = id
        self.next_level = self.id + 1

    @weak_and_lazy
    def next_level(self, id):
        return Level(id)
```

Besides the  tremendous memory requirements of  any individual level
it is impossible to load 'all' levels, since these are fundamentally
infinite in number.

So let's load the first two levels:

```python
>>> first = Level(1)
Loaded level: 1

>>> second = first.next_level
Loaded level: 2
```

Hey, it works! Can the second level be garbage collected even if the
first one stays alive?

```python
second_weak = weakref.ref(second)
assert second_weak() is not None
second = None
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

