# Test file for CS005 - Mutable Default Argument


def bad_list_default(items=[]):  # CS005 - mutable list default
    items.append("x")
    return items


def bad_dict_default(cache={}):  # CS005 - mutable dict default
    return cache


def bad_set_default(seen=set()):  # CS005 - mutable set default
    return seen


def bad_list_call(items=list()):  # CS005 - list() is also mutable
    return items


def bad_dict_call(data=dict()):  # CS005 - dict() is also mutable
    return data


def bad_kwonly(*, items=[]):  # CS005 - keyword-only with mutable default
    return items


def good_none_pattern(items=None):  # OK - correct pattern
    if items is None:
        items = []
    return items


def good_immutable_default(count=0, name="default", enabled=True):  # OK - immutable defaults
    return count, name, enabled


def good_tuple_default(items=()):  # OK - tuple is immutable
    return list(items)


def good_frozenset_default(items=frozenset()):  # OK - frozenset is immutable
    return items
