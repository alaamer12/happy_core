import functools
from typing import List, Any, Optional, Mapping, MutableMapping
from collections import OrderedDict


def find_first_index(sequence: List[Any], target: Any) -> Optional[int]:
    """Find the first index of 'target' in the sequence."""
    try:
        return sequence.index(target)
    except ValueError:
        return None  # Target not found


def find_last_index(sequence: List[Any], target: Any) -> Optional[int]:
    """Find the last index of 'target' in the sequence."""
    try:
        return len(sequence) - 1 - sequence[::-1].index(target)
    except ValueError:
        return None  # Target not found


def find_all_indices(sequence: List[Any], target: Any) -> List[int]:
    """Find all indices of 'target' in the sequence."""
    return [index for index, value in enumerate(sequence) if value == target]


def find_next_indices(sequence: List[Any], target: Any, start_index: int = 0) -> List[int]:
    """Find all indices of 'target' in the sequence after 'start_index'."""
    return [index for index, value in enumerate(sequence[start_index:], start=start_index) if value == target]


def replace_all(sequence: List[Any], target: Any, replacement: Any) -> List[Any]:
    """Replace all occurrences of 'target' with 'replacement' in the sequence."""
    return [replacement if value == target else value for value in sequence]


def remove_all(sequence: List[Any], target: Any) -> List[Any]:
    """Remove all occurrences of 'target' from the sequence."""
    return [value for value in sequence if value != target]


def find_all(sequence: List[Any], target: Any) -> List[Any]:
    """Find all occurrences of 'target' in the sequence."""
    return [value for value in sequence if value == target]


class ComplexTypeValidator:
    def __init__(self, value, expected_type):
        self.value = value
        self.expected_type = expected_type

    def validate(self) -> bool:
        if isinstance(self.expected_type, type):
            return isinstance(self.value, self.expected_type)
        _types = [list, dict, set, tuple]
        if self.expected_type in _types:
            _validate_type = getattr(self, f"_validate_{self.expected_type.__name__.lower()}_type")
            return _validate_type()
        return False

    def _validate_list_type(self) -> bool:
        if not isinstance(self.value, list) or len(self.expected_type) != 1:
            return False
        return all(ComplexTypeValidator(v, self.expected_type[0]).validate() for v in self.value)

    def _validate_dict_type(self) -> bool:
        if not isinstance(self.value, dict) or len(self.expected_type) != 1:
            return False
        key_type, value_type = list(self.expected_type.items())[0]
        return all(ComplexTypeValidator(k, key_type).validate() and ComplexTypeValidator(v, value_type).validate()
                   for k, v in self.value.items())

    def _validate_set_type(self) -> bool:
        if not isinstance(self.value, set) or len(self.expected_type) != 1:
            return False
        element_type = list(self.expected_type)[0]
        return all(ComplexTypeValidator(e, element_type).validate() for e in self.value)

    def _validate_tuple_type(self) -> bool:
        if not isinstance(self.value, tuple) or len(self.value) != len(self.expected_type):
            return False
        return all(ComplexTypeValidator(v, t).validate() for v, t in zip(self.value, self.expected_type))


@functools.total_ordering
class Constant:
    def __init__(self, **kwargs):
        self.__initialize_constants(**kwargs)

    def __initialize_constants(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

    def __setattr__(self, key, value):
        raise AttributeError("Cannot modify a constant")

    def __delattr__(self, key):
        raise AttributeError("Cannot delete a constant")

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Constant) and self.__dict__ == other.__dict__

    def __lt__(self, other):
        if not isinstance(other, Constant):
            return NotImplemented
        return tuple(sorted(self.__dict__.items())) < tuple(sorted(other.__dict__.items()))


@functools.total_ordering
class Pointer:
    def __init__(self, value=None):
        """Initialize the pointer with a value."""
        self._value = [value]  # Use a list to hold the reference

    def get(self):
        """Dereference the pointer to access the value."""
        return self._value[0]

    def set(self, value):
        """Dereference the pointer and set the new value."""
        self._value[0] = value

    def address(self):
        """Return the 'address' of the pointer, which in this case is its own id."""
        return id(self._value)

    def point_to(self, other_pointer):
        """Point this pointer to the memory location of another pointer."""
        if isinstance(other_pointer, Pointer):
            self._value = other_pointer._value
        else:
            raise TypeError("point_to expects another Pointer instance")

    def is_null(self):
        """Check if the pointer is null (i.e., points to None)."""
        return self._value[0] is None

    def __str__(self):
        """String representation showing the value and the 'address'."""
        return f"{self.__class__.__name__}(value={self._value[0]}, address={self.address()})"

    def __repr__(self):
        return self.__str__()

    def __del__(self):
        self._value[0] = None

    def __lt__(self, other):
        if not isinstance(other, Pointer):
            return NotImplemented
        return self.get() < other.get()


class CaseInsensitiveDict(MutableMapping):
    def __init__(self, data=None, **kwargs):
        self._store = OrderedDict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def __contains__(self, key):
        return key.lower() in self._store

    def __eq__(self, other):
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.items()) == dict(other.items())

    def lower_keys(self):
        """Like keys(), but with all lowercase keys."""
        return (keyval[0] for keyval in self._store.values())

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return ((lowerkey, keyval[1]) for (lowerkey, keyval) in self._store.items())

    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))


class LookupDict(dict):
    """Dictionary lookup object."""

    def __init__(self, name=None):
        self.name = name
        super().__init__()

    def __repr__(self):
        return f"<lookup '{self.name}'>"

    def __getitem__(self, key):
        return self.__dict__.get(key, None)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)
