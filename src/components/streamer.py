import signal
from multiprocessing import Queue

import cv2

from src.components.base_component import BaseComponent
from src.config.settings import Settings
from src.utils.ipc_utils import IPCMessage


class Streamer(BaseComponent):
    def __init__(self, video_path: str, output_queue: Queue):
        super().__init__("Streamer")
        self.video_path = video_path
        self.output_queue = output_queue
        self.terminate = False

    def handle_termination(self, signum, frame):
        self.terminate = True

    def run(self):
        signal.signal(signal.SIGINT, self.handle_termination)
        signal.signal(signal.SIGTERM, self.handle_termination)

        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            self.output_queue.put(IPCMessage(None, is_last=True))
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_delay = 1.0 / fps if fps > 0 else Settings.FRAME_DELAY

        try:
            frame_count = 0
            while not self.terminate:
                ret, frame = cap.read()
                if not ret:
                    self.output_queue.put(IPCMessage(None, is_last=True))
                    break

                frame_count += 1
                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

                self.measure_execution(
                    lambda: self.output_queue.put(
                        IPCMessage(
                            frame=frame,
                            timestamp=timestamp,
                            frame_number=frame_count
                        )
                    )
                )

        finally:
            cap.release()
