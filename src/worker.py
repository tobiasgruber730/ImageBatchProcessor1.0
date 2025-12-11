import threading
import queue
import os
import logging
from PIL import Image


class ImageWorker(threading.Thread):
    """
    A Consumer Thread that processes images from the queue.
    Inherits from threading.Thread for OOP structure.
    """

    def __init__(self, thread_id: int, task_queue: queue.Queue, config: dict, stop_event: threading.Event):
        """
        Initializes the worker thread.

        Args:
            thread_id (int): Unique identifier for the worker.
            task_queue (queue.Queue): Shared queue to pull tasks from.
            config (dict): Application configuration settings.
            stop_event (threading.Event): Event to signal thread termination.
        """
        super().__init__()
        self.thread_id = thread_id
        self.task_queue = task_queue
        self.config = config
        self.stop_event = stop_event
        self.name = f"Worker-{thread_id}"

    def run(self):
        """
        Main execution loop of the thread.
        Continuously pulls tasks from the queue until the stop signal is set.
        """
        logging.info(f"{self.name} started.")

        while not self.stop_event.is_set() or not self.task_queue.empty():
            try:
                # 1. Attempt to retrieve a task from the queue with a timeout.
                # The timeout prevents blocking indefinitely if the producer stops.
                file_name = self.task_queue.get(timeout=1)
            except queue.Empty:
                # 2. Critical: If the queue is empty, restart the loop to check the stop_event.
                # Do NOT call task_done() here as no task was retrieved.
                continue

            # 3. Process the retrieved image.
            self.process_image(file_name)

            # 4. Signal that the task is complete.
            # This is only called if step 1 succeeded.
            self.task_queue.task_done()

    def process_image(self, file_name: str):
        """
        Handles the logic for resizing and saving the image.

        Args:
            file_name (str): The name of the file to process.
        """
        input_path = os.path.join(self.config['source_folder'], file_name)
        output_path = os.path.join(self.config['destination_folder'], file_name)

        try:
            logging.info(f"{self.name}: Processing {file_name}")

            with Image.open(input_path) as img:
                # Resize logic based on configuration
                new_size = (self.config['resize_width'], self.config['resize_height'])
                img_resized = img.resize(new_size)
                # Save the result to the output directory
                img_resized.save(output_path)

            logging.info(f"{self.name}: Finished {file_name}")

        except Exception as e:
            # Catch all exceptions to prevent the thread from crashing
            logging.error(f"{self.name}: Error processing {file_name}: {e}")