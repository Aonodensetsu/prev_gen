from __future__ import annotations


class Raises:
    """
    Catch a specific exception type and keep the result

    All other types still get raised

    :param catch: the chosen exception type(s)

    Attributes:
        raised: whether the chosen exception was raised
    """
    catch: tuple
    raised: bool

    def __init__(self, *catch):
        self.catch = catch

    def __enter__(self) -> Raises:
        self.raised = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type in self.catch:
            self.raised = True
            return True
        return False


def closeEnough(*args, digits: int = 4) -> bool:
    """
    :param args: Collections of floats
    :param digits: The amount of digits to round to
    :return: The values are equal when rounded to n digits
    """
    val = tuple(round(i, digits) for i in args[0])
    for i in args[1:]:
        if not tuple(round(x, digits) for x in i) == val:
            return False
    return True
