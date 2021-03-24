import argparse
import io
import itertools


Empty = object()

class PrimedIterator:

    @classmethod
    def prime(cls, iterator, default=Empty):
        """Retrieve the first item from the given iterator and return a new
        iterator over *all* elements.

        No elements from the original iterator are missed by the returned
        iterator.

        Rather, the iterator is thereby initiated, and tested for emptiness.

        This can be a useful helper in emptiness checks (which must then
        construct this secondary iterator wrapper over the first, retrieved
        element and the remainder).

        This may also be useful in initializing complex generator functions
        (e.g. those with buffers), without retrieving more than one item
        from its stream, and maintaining its full contents.

        If a second argument, the default, is given, and the iterator is
        already empty/exhausted, then this default is returned instead of
        raising StopIteration (as with `next`).

        """
        try:
            first = next(iterator)
        except StopIteration:
            if default is not Empty:
                return default

            raise

        return cls(first, iterator)

    def __init__(self, first, iterator):
        self.iterator = iterator
        self.__chain__ = itertools.chain((first,), iterator)

    def __iter__(self):
        return self.__chain__

    def __repr__(self):
        return f'({self.__class__.__name__}: {self.iterator!r})'

prime_iterator = PrimedIterator.prime


class HelpAction(argparse.Action):
    """Pluggable "help" action.

    Based on the built-in "help" action, enabling the definition of
    additional "--help-*" flags.

    Help output must be printed by the given callable `help_action`.

    When the flag is set, `help_action` is invoked and then the process
    is exited.

    """
    def __init__(self,
                 option_strings,
                 *,
                 help_action,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

        self.help_action = help_action

    def __call__(self, parser, namespace, values, option_string=None):
        self.help_action(parser, namespace, values, option_string)
        parser.exit()


class NumericRangeType:
    """Argument type validating that given value is of configured
    numeric type and bounds.

    Bounds may be specified as either `list` or `tuple`, the convention
    indicating whether bounds are "inclusive" or "non-inclusive",
    respectively.

    Either the lower or upper bound may be specified as `None`,
    indicating no bound.

    For example:

        parser.add_argument(
            '--test-size',
            default=0.3,
            metavar='FLOAT',
            type=NumericRangeType(float, (0, 1)),
        )

    The above argument, `--test-size`, will cast its input to `float`,
    (or print an error for non-float input). Moreover, a "not in range"
    error will be printed for inputs equal to zero or equal to or
    greater than one.

        parser.add_argument(
            '--threads',
            default=1,
            metavar='INTEGER',
            type=NumericRangeType(int, (0, None)),
        )

    In the above example, inputs are instead enforced as `int`; and,
    there is _only_ a lower bound -- inputs must only be greater than
    zero.

        parser.add_argument(
            '-q', '--quality',
            default=0,
            metavar='INTEGER',
            type=NumericRangeType(int, [0, 4]),
        )

    Arguments may also be given inclusive bounds, as above -- inputs to
    this example must be greater than or equal to zero, and less than or
    equal to four.

    """
    bounds_message = "upper and lower bounds must be list or tuple of two elements"

    def __init__(self, numeric_type, bounds):
        self.numeric_type = numeric_type

        try:
            (self.lower_bound, self.upper_bound) = bounds
        except ValueError as exc:
            raise ValueError(f"{self.bounds_message} not: {bounds!r}") from exc
        except TypeError as exc:
            raise TypeError(
                f"{self.bounds_message} not {bounds.__class__.__name__}: {bounds!r}"
            ) from exc

        if isinstance(bounds, tuple):
            self.inclusive = False
        elif isinstance(bounds, list):
            self.inclusive = True
        else:
            raise TypeError(f"{self.bounds_message} not {bounds.__class__.__name__}: {bounds!r}")

    def __call__(self, value):
        try:
            number = self.numeric_type(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"not {self.numeric_type.__name__}: {value!r}")

        if self.inclusive:
            if (
                (self.lower_bound is not None and number < self.lower_bound) or
                (self.upper_bound is not None and number > self.upper_bound)
            ):
                raise argparse.ArgumentTypeError(
                    f"not in range [{self.lower_bound}, {self.upper_bound}]: {number!r}"
                )
        else:
            if (
                (self.lower_bound is not None and number <= self.lower_bound) or
                (self.upper_bound is not None and number >= self.upper_bound)
            ):
                raise argparse.ArgumentTypeError(
                    f"not in range ({self.lower_bound}, {self.upper_bound}): {number!r}"
                )

        return number


class NamedStringIO(io.StringIO):
    """StringIO featuring a `name` attribute to reflect the path
    represented by its contents.

    """
    def __init__(self, initial_value='', newline='\n', name=None):
        super().__init__(initial_value, newline)
        self.name = name


class NamedBytesIO(io.BytesIO):
    """BytesIO featuring a `name` attribute to reflect the path
    represented by its contents.

    """
    def __init__(self, initial_bytes=b'', name=None):
        super().__init__(initial_bytes)
        self.name = name
