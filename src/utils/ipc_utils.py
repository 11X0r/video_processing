from dataclasses import dataclass
from typing import List, Optional

import numpy.typing as npt


@dataclass
class Detection:
    x: int
    y: int
    width: int
    height: int


@dataclass
class IPCMessage:
    frame: Optional[npt.NDArray] = None
    timestamp: Optional[float] = None
    detections: List[Detection] = None
    is_last: bool = False
    frame_number: int = 0

    def __post_init__(self):
        if self.detections is None:
            self.detections = []
