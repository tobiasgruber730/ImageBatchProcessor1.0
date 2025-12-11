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
        super().__init__()
        self.thread_id = thread_id
        self.task_queue = task_queue
        self.config = config
        self.stop_event = stop_event
        self.name = f"Worker-{thread_id}"

    def run(self):
        """
        Main loop of the thread. Automatically called when thread.start() is invoked.
        """
        logging.info(f"{self.name} started.")

        while not self.stop_event.is_set() or not self.task_queue.empty():
            try:
                # 1. Pokusíme se vzít úkol z fronty
                file_name = self.task_queue.get(timeout=1)
            except queue.Empty:
                # 2. DŮLEŽITÉ: Pokud je fronta prázdná, okamžitě jdeme na začátek smyčky.
                # NIKDY v tomto případě nesmíme volat task_done()!
                continue

            # 3. Pokud jsme tady, znamená to, že 'get' neselhal a máme soubor.
            self.process_image(file_name)

            # 4. Teprve teď nahlásíme splnění úkolu.
            # Tento řádek se provede jen tehdy, když jsme úspěšně prošli bodem 1.
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