from queue import Queue
from threading import Thread

incident_queue = Queue()

def start_worker(process_fn):
    def worker():
        while True:
            payload = incident_queue.get()
            if payload is None:
                break
            process_fn(payload)
            incident_queue.task_done()

    Thread(target=worker, daemon=True).start()
