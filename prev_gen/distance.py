from dataclasses import dataclass
from typing import Iterator


@dataclass(slots=True)
class Distance:
    """
    Absolute distance in pixels
    used for position and size when placing tiles in an image
    and for the size of the image itself

    Attributes:
        x: Horizontal offset

        y: Vertical offset
    """
    x: int
    y: int

    def __iter__(self) -> Iterator[int]:
        """
        Allows conversion to a tuple
        """
        return iter((self.x, self.y))
