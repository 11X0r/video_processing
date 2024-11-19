import time
from multiprocessing import Process

from src.utils.monitoring import ComponentMetrics


class BaseComponent(Process):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.metrics = ComponentMetrics()
        self.start_time = time.time()

    def measure_execution(self, func):
        start_time = time.time()
        result = func()
        self.metrics.update_processing_time(time.time() - start_time)
        return result
