# Test file for CS002 - Placeholder Code in Production


def not_implemented_yet():
    # TODO: implement this function
    pass  # CS002 should trigger


def stub_function():
    """This does something important."""
    ...  # NO CS002 - no TODO/FIXME present (per spec: "paired with")


def raises_not_implemented():
    # FIXME: finish this
    raise NotImplementedError  # CS002


def raises_not_implemented_with_message():
    # TODO: complete implementation
    raise NotImplementedError("Not done yet")  # CS002


def actually_implemented():
    # TODO: optimize this later
    return compute_value()  # OK - has real implementation


def has_pass_but_does_something():
    x = calculate()
    if not x:
        pass  # This pass is inside logic, not a stub
    return x
