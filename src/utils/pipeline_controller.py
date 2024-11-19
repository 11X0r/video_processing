from dataclasses import dataclass
from enum import Enum
from multiprocessing import Event
from typing import Dict

from src.utils.monitoring import ComponentMetrics


class PipelineState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class PipelineStatus:
    state: PipelineState
    component_metrics: Dict[str, ComponentMetrics]
    error_message: str = None


class PipelineController:
    def __init__(self):
        self.state = PipelineState.INITIALIZING
        self.pause_event = Event()
        self.stop_event = Event()
        self.component_metrics = {}

    def register_component(self, name: str, metrics: ComponentMetrics):
        self.component_metrics[name] = metrics

    def get_status(self) -> PipelineStatus:
        return PipelineStatus(
            state=self.state,
            component_metrics=self.component_metrics
        )

    def pause(self):
        self.state = PipelineState.PAUSED
        self.pause_event.set()

    def resume(self):
        self.state = PipelineState.RUNNING
        self.pause_event.clear()

    def stop(self):
        self.state = PipelineState.STOPPING
        self.stop_event.set()
