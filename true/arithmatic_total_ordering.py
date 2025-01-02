from operator import pow, add, sub, truediv, floordiv, mod, mul


def safe_arithmetic(func):
    """Simple decorator to handle ArithmeticError exceptions."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ArithmeticError:
            return NotImplemented

    return wrapper


@safe_arithmetic
def _do_arithmatic(self, other, op, derived_op):
    op_result = getattr(type(self), derived_op)(self, other)
    if op_result is NotImplemented:
        return op_result
    return op(self.value, other.value)


class FixIDEComplain:
    """A mixin class to fix IDE complaints about dynamically added methods, with on-demand generation."""

    def __getattr__(self, name):
        """Generate missing operators dynamically."""
        if name in _convert:
            # Generate the dynamic method on-the-fly using the _convert dictionary
            for opname, opfunc in _convert[name]:
                setattr(self, opname, opfunc)
            # Once generated, return the first operation function
            return getattr(self, name)
        raise AttributeError(f"{type(self).__name__} object has no attribute '{name}'")


def _sub_from_add(self, other):
    return _do_arithmatic(self, other, sub, '__add__')


def _floordiv_from_add(self, other):
    return _do_arithmatic(self, other, floordiv, '__add__')


def _truediv_from_add(self, other):
    return _do_arithmatic(self, other, truediv, '__add__')


def _mul_from_add(self, other):
    return _do_arithmatic(self, other, mul, '__add__')


def _mod_from_add(self, other):
    return _do_arithmatic(self, other, mod, '__add__')


def _pow_from_add(self, other):
    return _do_arithmatic(self, other, pow, '__add__')


def _iadd_from_add(self, other):
    result = self + other
    if result is NotImplemented:
        return NotImplemented
    self.value = result.value
    return self


def _radd_from_add(self, other):
    return type(self)(other + self.value)


def _floordiv_from_truediv(self, other):
    return _do_arithmatic(self, other, floordiv, '__truediv__')


def _add_from_truediv(self, other):
    return _do_arithmatic(self, other, add, '__truediv__')


def _mul_from_truediv(self, other):
    return _do_arithmatic(self, other, mul, '__truediv__')


def _mod_from_truediv(self, other):
    return _do_arithmatic(self, other, mod, '__truediv__')


def _pow_from_truediv(self, other):
    return _do_arithmatic(self, other, pow, '__truediv__')


def _sub_from_truediv(self, other):
    return _do_arithmatic(self, other, sub, '__truediv__')


def _itruediv_from_truediv(self, other):
    op_result = type(self).__truediv__(self, other)
    if op_result is NotImplemented:
        return NotImplemented
    self.value /= op_result
    return self


def _rtruediv_from_truediv(self, other):
    return type(self)(other / self.value)


def _add_from_sub(self, other):
    return _do_arithmatic(self, other, add, '__sub__')


def _mul_from_sub(self, other):
    return _do_arithmatic(self, other, mul, '__sub__')


def _truediv_from_sub(self, other):
    return _do_arithmatic(self, other, truediv, '__sub__')


def _floordiv_from_sub(self, other):
    return _do_arithmatic(self, other, floordiv, '__sub__')


def _mod_from_sub(self, other):
    return _do_arithmatic(self, other, mod, '__sub__')


def _pow_from_sub(self, other):
    return _do_arithmatic(self, other, pow, '__sub__')


def _isub_from_sub(self, other):
    op_result = type(self).__sub__(self, other)
    if op_result is NotImplemented:
        return NotImplemented
    self.value -= op_result
    return self


def _rsub_from_sub(self, other):
    return type(self)(other - self.value)


def _add_from_mul(self, other):
    return _do_arithmatic(self, other, add, '__mul__')


def _truediv_from_mul(self, other):
    return _do_arithmatic(self, other, truediv, '__mul__')


def _sub_from_mul(self, other):
    return _do_arithmatic(self, other, sub, '__mul__')


def _pow_from_mul(self, other):
    return _do_arithmatic(self, other, pow, '__mul__')


def _floordiv_from_mul(self, other):
    return _do_arithmatic(self, other, floordiv, '__mul__')


def _mod_from_mul(self, other):
    return _do_arithmatic(self, other, mod, '__mul__')


def _imul_from_mul(self, other):
    op_result = type(self).__mul__(self, other)
    if op_result is NotImplemented:
        return NotImplemented
    self.value *= op_result
    return self


def _rmul_from_mul(self, other):
    return type(self)(other + self.value)


_convert = {
    '__add__': [
        ('__sub__', _sub_from_add),
        ('__iadd__', _iadd_from_add),
        ('__radd__', _radd_from_add),
        ('__mul__', _mul_from_add),
        ('__truediv__', _truediv_from_add),
        ('__floordiv__', _floordiv_from_add),
        ('__mod__', _mod_from_add),
        ('__pow__', _pow_from_add)
    ],
    '__sub__': [
        ('__add__', _add_from_sub),
        ('__isub__', _isub_from_sub),
        ('__radd__', _rsub_from_sub),
        ('__mul__', _mul_from_sub),
        ('__truediv__', _truediv_from_sub),
        ('__floordiv__', _floordiv_from_sub),
        ('__mod__', _mod_from_sub),
        ('__pow__', _pow_from_sub)
    ],
    '__mul__': [
        ('__add__', _add_from_mul),
        ('__sub__', _sub_from_mul),
        ('__imul__', _imul_from_mul),
        ('__rmul__', _rmul_from_mul),
        ('__truediv__', _truediv_from_mul),
        ('__floordiv__', _floordiv_from_mul),
        ('__mod__', _mod_from_mul),
        ('__pow__', _pow_from_mul)
    ],
    '__truediv__': [
        ('__add__', _add_from_truediv),
        ('__sub__', _sub_from_truediv),
        ('__floordiv__', _floordiv_from_truediv),
        ('__mul__', _mul_from_truediv),
        ('__itruediv__', _itruediv_from_truediv),
        ('__rtruediv__', _rtruediv_from_truediv),
        ('__mod__', _mod_from_truediv),
        ('__pow__', _pow_from_truediv)
    ],
    # ...
}


def arithmatic_total_ordering(cls):
    """Class decorator that fills in missing ordering methods"""
    # Find which ordering operation(s) are defined
    roots = {op for op in _convert if getattr(cls, op, None) is not getattr(object, op, None)}
    if not roots:
        raise ValueError('must define at least one ordering operation: + - * /')

    # Add all related operations based on defined ones
    for root in roots:
        for opname, opfunc in _convert[root]:
            if opname not in roots:
                opfunc.__name__ = opname
                setattr(cls, opname, opfunc)
    return cls