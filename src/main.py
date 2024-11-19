import logging
import signal
import sys
from multiprocessing import Queue
from pathlib import Path

from src.components.detector import Detector
from src.components.presenter import Presenter
from src.components.streamer import Streamer
from src.config.settings import Settings
from src.utils.pipeline_controller import PipelineController, PipelineState


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def terminate_processes(processes):
    for process in processes:
        if process.is_alive():
            process.terminate()
            process.join()


def drain_queue(queue: Queue):
    while not queue.empty():
        try:
            queue.get_nowait()
        except:
            break


def main(video_path: str):
    setup_logging()

    if not Path(video_path).exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    controller = PipelineController()

    def signal_handler(signum, frame):
        controller.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    streamer_to_detector = Queue(maxsize=Settings.QUEUE_SIZE)
    detector_to_presenter = Queue(maxsize=Settings.QUEUE_SIZE)

    processes = []

    try:
        streamer = Streamer(video_path, streamer_to_detector)
        detector = Detector(streamer_to_detector, detector_to_presenter)
        presenter = Presenter(detector_to_presenter)

        processes.extend([streamer, detector, presenter])

        for process in processes:
            process.start()

        for process in processes:
            process.join()

    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt, shutting down...")
        controller.stop()
    except Exception as e:
        logging.error(f"Pipeline error: {str(e)}")
        controller.state = PipelineState.ERROR
        raise
    finally:
        terminate_processes(processes)
        for queue in [streamer_to_detector, detector_to_presenter]:
            drain_queue(queue)
            queue.close()
            queue.join_thread()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src.main <video_path>")
        sys.exit(1)

    try:
        main(sys.argv[1])
    except FileNotFoundError as e:
        logging.error(str(e))
        sys.exit(1)
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)
