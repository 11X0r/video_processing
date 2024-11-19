import logging
import signal
from multiprocessing import Queue
from typing import List

import cv2
import numpy as np

from src.components.base_component import BaseComponent
from src.config.settings import Settings
from src.utils.ipc_utils import IPCMessage, Detection


class Detector(BaseComponent):
    def __init__(self, input_queue: Queue, output_queue: Queue):
        super().__init__("Detector")
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.terminate = False

    def handle_termination(self, signum, frame):
        self.terminate = True

    def detect_motion(self, frame: np.ndarray) -> List[Detection]:
        fg_mask = self.background_subtractor.apply(frame)
        _, thresh = cv2.threshold(fg_mask, Settings.DETECTOR_THRESHOLD, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if Settings.MIN_CONTOUR_AREA < area < Settings.MAX_CONTOUR_AREA:
                x, y, w, h = cv2.boundingRect(contour)
                detections.append(Detection(x, y, w, h))
        return detections

    def run(self):
        signal.signal(signal.SIGINT, self.handle_termination)
        signal.signal(signal.SIGTERM, self.handle_termination)

        try:
            while not self.terminate:
                try:
                    message = self.input_queue.get(timeout=1)
                except:
                    continue

                if message.is_last:
                    self.output_queue.put(message)
                    break

                detections = self.measure_execution(
                    lambda: self.detect_motion(message.frame)
                )

                self.output_queue.put(
                    IPCMessage(
                        frame=message.frame,
                        timestamp=message.timestamp,
                        detections=detections,
                        frame_number=message.frame_number
                    )
                )
        except Exception as e:
            logging.error(f"Detector error: {str(e)}")
            raise
