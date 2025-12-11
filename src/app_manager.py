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
    Acts as the PRODUCER in the Producer-Consumer pattern.
    """

    def __init__(self):
        # Setup paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_dir, 'conf', 'config.json')

        # Load Config
        loader = ConfigLoader(self.config_path)
        self.config = loader.load_config()
        self._resolve_paths()

        # Setup Logging
        self._setup_logging()

        # Synchronization primitives
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

        # Ensure output dir exists
        os.makedirs(self.config['destination_folder'], exist_ok=True)

        # 1. Start Consumers (Workers)
        self._start_workers()

        # 2. Run Producer (Main Thread)
        self._produce_tasks()

        # 3. Wait for completion
        self._wait_for_completion()

        logging.info("--- Application Finished ---")

    def _start_workers(self):
        """
        Initializes and starts worker threads.
        Determines the number of threads based on CPU cores if config is set to 0.
        """
        config_threads = self.config['number_of_threads']

        # Logic for auto-detection
        if config_threads <= 0:
            # os.cpu_count() returns the number of logical CPUs.
            # If it cannot be determined, we default to 4 as a safe fallback.
            cpu_count = os.cpu_count() or 4
            logging.info(f"Auto-configuration: Detected {cpu_count} CPU cores.")
            count = cpu_count
        else:
            logging.info(f"Using manual configuration: {config_threads} threads.")
            count = config_threads

        logging.info(f"Spawning {count} worker threads...")

        for i in range(count):
            worker = ImageWorker(i + 1, self.task_queue, self.config, self.stop_event)
            worker.start()
            self.threads.append(worker)

    def _produce_tasks(self):
        """
        Scans the input folder, validates files, and fills the queue.
        This represents the PRODUCER logic.
        """
        src = self.config['source_folder']
        logging.info(f"Producer: Scanning folder: {src}")

        added_count = 0
        skipped_count = 0

        try:
            # Iterate over all entries in the directory
            for entry in os.listdir(src):
                if self._validate_input_file(entry):
                    self.task_queue.put(entry)
                    added_count += 1
                else:
                    skipped_count += 1
                    logging.warning(f"Producer: Skipped invalid file: {entry}")

            logging.info(f"Producer finished: {added_count} tasks added, {skipped_count} skipped.")

        except FileNotFoundError:
            logging.error(f"Source folder not found: {src}")
        except PermissionError:
            logging.error(f"Permission denied accessing folder: {src}")

    def _validate_input_file(self, file_name: str) -> bool:
        """
        Validates if the file is suitable for processing.

        Criteria:
        1. Must be a file (not a directory).
        2. Must have a valid image extension.
        3. Must not be empty (size > 0 bytes).

        Args:
            file_name (str): Name of the file to check.

        Returns:
            bool: True if valid, False otherwise.
        """
        full_path = os.path.join(self.config['source_folder'], file_name)

        # Check 1: Is it a file?
        if not os.path.isfile(full_path):
            return False

        # Check 2: Valid extension?
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        if not file_name.lower().endswith(valid_extensions):
            return False

        # Check 3: Is file empty? (Zero bytes files cause crashes)
        if os.path.getsize(full_path) == 0:
            return False

        return True

    def _wait_for_completion(self):
        """Waits for the queue to empty and stops threads."""
        self.task_queue.join()  # Block until queue is empty
        logging.info("All tasks in queue processed. Stopping threads...")

        self.stop_event.set()  # Signal threads to stop

        for t in self.threads:
            t.join()  # Wait for threads to close