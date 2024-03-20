# Unravelling the `dataclasses`

### Here is the source code of Python 3.11

```py
def dataclass(cls=None, /, *, init=True, repr=True, eq=True, order=False,
              unsafe_hash=False, frozen=False, match_args=True,
              kw_only=False, slots=False, weakref_slot=False):
    """Add dunder methods based on the fields defined in the class.

    Examines PEP 526 __annotations__ to determine fields.

    If init is true, an __init__() method is added to the class. If repr
    is true, a __repr__() method is added. If order is true, rich
    comparison dunder methods are added. If unsafe_hash is true, a
    __hash__() method is added. If frozen is true, fields may not be
    assigned to after instance creation. If match_args is true, the
    __match_args__ tuple is added. If kw_only is true, then by default
    all fields are keyword-only. If slots is true, a new class with a
    __slots__ attribute is returned.
    """

    def wrap(cls):
        return _process_class(cls, init, repr, eq, order, unsafe_hash,
                              frozen, match_args, kw_only, slots,
                              weakref_slot)

    # See if we're being called as @dataclass or @dataclass().
    if cls is None:
        # We're called with parens.
        return wrap

    # We're called as @dataclass without parens.
    return wrap(cls)
```

### Usage

1. Create class in a simple way
2. Reuse common function like `__eq__`/`__str__`/`__repr__`
3. Custom init function like `__post_init__`
4. Take some parameters to make our class much powerful
5. Validating data With dataclass constraints

Just like this:

```py
@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False,       frozen=False, match_args=True, kw_only=False, slots=False, weakref_slot=False)
class C:
    ...
```


#### `kw_only` means I have to add kw_name when initialize a instance
#### `frozen` means immutable once instantiated
#### `slots` means a much faster data type but not a good choice when inheriting
