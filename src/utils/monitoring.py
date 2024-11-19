import time
from dataclasses import dataclass
from typing import List


@dataclass
class ComponentMetrics:
    start_time: float = 0
    processing_times: List[float] = None
    frame_count: int = 0
    dropped_frames: int = 0

    def __post_init__(self):
        self.start_time = time.time()
        self.processing_times = []

    def update_processing_time(self, processing_time: float):
        self.processing_times.append(processing_time)
        self.frame_count += 1

    def get_average_processing_time(self) -> float:
        if not self.processing_times:
            return 0
        return sum(self.processing_times) / len(self.processing_times)

    def get_fps(self) -> float:
        elapsed_time = time.time() - self.start_time
        return self.frame_count / elapsed_time if elapsed_time > 0 else 0
