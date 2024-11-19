import signal
import time
from multiprocessing import Queue
from typing import List

import cv2
import numpy as np

from src.components.base_component import BaseComponent
from src.config.settings import Settings
from src.utils.ipc_utils import Detection


class Presenter(BaseComponent):
    def __init__(self, input_queue: Queue):
        super().__init__("Presenter")
        self.input_queue = input_queue
        self.last_frame_time = None
        self.frame_count = 0

    def apply_blur(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        blurred_frame = frame.copy()
        for detection in detections:
            roi = blurred_frame[
                  detection.y:detection.y + detection.height,
                  detection.x:detection.x + detection.width
                  ]
            blurred_roi = cv2.GaussianBlur(
                roi,
                Settings.BLUR_KERNEL_SIZE,
                Settings.SIGMA_X
            )
            blurred_frame[
            detection.y:detection.y + detection.height,
            detection.x:detection.x + detection.width
            ] = blurred_roi
        return blurred_frame

    def draw_detections(
            self,
            frame: np.ndarray,
            detections: List[Detection],
            timestamp: float
    ) -> np.ndarray:
        cv2.putText(
            frame,
            f"Time: {timestamp:.2f}s",
            Settings.TIMESTAMP_POSITION,
            cv2.FONT_HERSHEY_SIMPLEX,
            Settings.FONT_SCALE,
            Settings.TIMESTAMP_COLOR,
            Settings.FONT_THICKNESS
        )

        for detection in detections:
            cv2.rectangle(
                frame,
                (detection.x, detection.y),
                (detection.x + detection.width, detection.y + detection.height),
                Settings.DETECTION_BOX_COLOR,
                Settings.DETECTION_BOX_THICKNESS
            )
        return frame

    def maintain_fps(self, timestamp: float):
        if self.last_frame_time is not None:
            time_diff = timestamp - self.last_frame_time
            if time_diff < Settings.FRAME_DELAY:
                time.sleep(Settings.FRAME_DELAY - time_diff)
        self.last_frame_time = timestamp

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        cv2.namedWindow("Video Feed", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Video Feed", Settings.DISPLAY_WIDTH, Settings.DISPLAY_HEIGHT)

        try:
            while True:
                try:
                    message = self.input_queue.get(timeout=1)
                except:
                    continue

                if message.is_last:
                    break

                self.frame_count += 1

                blurred_frame = self.measure_execution(
                    lambda: self.apply_blur(message.frame, message.detections)
                )

                display_frame = self.draw_detections(
                    blurred_frame,
                    message.detections,
                    message.timestamp
                )

                self.maintain_fps(message.timestamp)
                cv2.imshow("Video Feed", display_frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            cv2.destroyAllWindows()
