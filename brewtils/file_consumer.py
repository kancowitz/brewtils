import json
import os

import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from brewtils.request_handling import RequestConsumerBase
from brewtils.schema_parser import SchemaParser


class FilePublisher(object):
    def __init__(self, directory):
        self._directory = directory

    def publish_request(self, request, **_):
        with open(os.path.join(self._directory, str(request.id)), mode="x") as f:
            json.dump(SchemaParser.serialize_request(request, to_string=False), f)


class FileRequestConsumer(RequestConsumerBase, FileSystemEventHandler):
    def __init__(self, directory, **kwargs):
        super(FileRequestConsumer, self).__init__(**kwargs)

        self._directory = directory
        self._observer = Observer()

    def run(self):
        self._observer.schedule(self, self._directory)
        self._observer.start()

        while not self.shutdown_event.is_set():
            time.sleep(1)

        self._observer.stop()
        self._observer.join()

    def stop(self):
        self.shutdown_event.set()

    def on_created(self, event):
        if event.is_directory:
            return None

        with open(event.src_path) as f:
            message = f.read()

        self._on_message_callback(message, {})
