from dataclasses import dataclass


@dataclass
class Settings:
    # Queue settings
    QUEUE_SIZE: int = 30

    # Video settings
    DEFAULT_FPS: float = 25.0
    FRAME_DELAY: float = 1.0 / DEFAULT_FPS

    # Detector settings
    DETECTOR_THRESHOLD: int = 30
    MIN_CONTOUR_AREA: int = 500
    MAX_CONTOUR_AREA: int = 30000

    # Presenter settings
    DISPLAY_WIDTH: int = 1280
    DISPLAY_HEIGHT: int = 720
    FONT_SCALE: float = 0.7
    FONT_THICKNESS: int = 2
    TIMESTAMP_POSITION: tuple = (10, 30)
    TIMESTAMP_COLOR: tuple = (255, 255, 255)
    DETECTION_BOX_COLOR: tuple = (0, 255, 0)
    DETECTION_BOX_THICKNESS: int = 2

    # Blur settings
    BLUR_KERNEL_SIZE: tuple = (15, 15)
    SIGMA_X: int = 0
