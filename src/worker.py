import threading
import queue
import os
import logging
import time
from PIL import Image


class ImageWorker(threading.Thread):
    """
    A Consumer Thread that processes images from the queue.
    Inherits from threading.Thread for OOP structure.
    """

    def __init__(self, thread_id: int, task_queue: queue.Queue, config: dict, stop_event: threading.Event):
        super().__init__()
        self.thread_id = thread_id
        self.task_queue = task_queue
        self.config = config
        self.stop_event = stop_event
        self.name = f"Worker-{thread_id}"  # Thread name for logging

    def run(self):
        """
        Main loop of the thread. Automatically called when thread.start() is invoked.
        """
        logging.info(f"{self.name} started.")

        while not self.stop_event.is_set() or not self.task_queue.empty():
            try:
                file_name = self.task_queue.get(timeout=1)
                self.process_image(file_name)
            except queue.Empty:
                continue
            finally:
                # If we processed a task, mark it as done
                if 'file_name' in locals():
                    self.task_queue.task_done()

    def process_image(self, file_name: str):
        """
        Actual logic for image manipulation.
        """
        input_path = os.path.join(self.config['source_folder'], file_name)
        output_path = os.path.join(self.config['destination_folder'], file_name)

        try:
            logging.info(f"{self.name}: Processing {file_name}")

            with Image.open(input_path) as img:
                new_size = (self.config['resize_width'], self.config['resize_height'])
                img_resized = img.resize(new_size)
                img_resized.save(output_path)

            logging.info(f"{self.name}: Finished {file_name}")

        except Exception as e:
            logging.error(f"{self.name}: Error processing {file_name}: {e}")