import os
import logging
import queue
import threading
from typing import List
from config_loader import ConfigLoader
from worker import ImageWorker


class BatchProcessorApp:
    """
    Main Application Controller.
    Manages the lifecycle of the application: initialization, execution, and cleanup.
    """

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_dir, 'conf', 'config.json')

        loader = ConfigLoader(self.config_path)
        self.config = loader.load_config()
        self._resolve_paths()

        self._setup_logging()

        self.task_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.threads: List[ImageWorker] = []

    def _resolve_paths(self):
        """Updates relative paths in config to absolute paths."""
        for key in ['source_folder', 'destination_folder', 'log_file']:
            self.config[key] = os.path.join(self.base_dir, self.config[key])

    def _setup_logging(self):
        """Initializes logging configuration."""
        os.makedirs(os.path.dirname(self.config['log_file']), exist_ok=True)
        logging.basicConfig(
            filename=self.config['log_file'],
            level=logging.INFO,
            format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logging.getLogger('').addHandler(console)

    def run(self):
        """
        Starts the application logic.
        """
        logging.info("--- Application Starting ---")

        os.makedirs(self.config['destination_folder'], exist_ok=True)

        self._start_workers()

        self._produce_tasks()

        self._wait_for_completion()

        logging.info("--- Application Finished ---")

    def _start_workers(self):
        """Initializes and starts worker threads."""
        count = self.config['number_of_threads']
        logging.info(f"Spawning {count} worker threads.")

        for i in range(count):
            worker = ImageWorker(i + 1, self.task_queue, self.config, self.stop_event)
            worker.start()
            self.threads.append(worker)

    def _produce_tasks(self):
        """Scans the input folder and fills the queue."""
        src = self.config['source_folder']
        logging.info(f"Scanning folder: {src}")

        try:
            files = [f for f in os.listdir(src) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            for f in files:
                self.task_queue.put(f)
            logging.info(f"Producer added {len(files)} tasks to queue.")
        except FileNotFoundError:
            logging.error("Source folder not found!")

    def _wait_for_completion(self):
        """Waits for the queue to empty and stops threads."""
        self.task_queue.join()
        self.stop_event.set()

        for t in self.threads:
            t.join()