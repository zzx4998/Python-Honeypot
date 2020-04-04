#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from database.connector import insert_file_change_events
from core.alert import info
from core.compatible import byte_to_str
from core.time_helper import now


def is_excluded(path, dirs):
    """
    if path is excluded in list of dirs/files

    :param path: path to check for exclude
    :param dirs: list of excludes
    :return: Boolean
    """
    for directory in dirs:
        if path.startswith(directory):
            return True
    return False


class containerFilesHandler(FileSystemEventHandler):
    def __init__(self):
        self.log_filename = None
        self.EXCLUDES = None
        self.module_name = None

    @staticmethod
    def on_any_event(event):
        if not (event.event_type == 'modified' and event.is_directory) and is_excluded(event.src_path, self.EXCLUDES):
            # todo: self is not accessible from here, must be fix before merging the PR. not sure if we should use
            # super() or something else
            insert_file_change_events(
                byte_to_str(event.src_path),
                byte_to_str(event.event_type),
                self.module_name,
                now()
            )
            info("Event on a file: " + byte_to_str(event.event_type) + " , path: " + byte_to_str(event.src_path))


class fileMonitor:
    def __init__(self):
        self.observer = Observer()
        self.log_filename = None
        self.log_filename_dump = None
        self.stop_execution = False
        self.DIRECTORY_TO_WATCH = None
        self.EXCLUDES = []
        self.module_name = None

    def stop(self):
        self.self_execution = True
        self.observer.stop()

    def run(self):
        event_handler = containerFilesHandler()
        event_handler.log_filename = self.log_filename
        event_handler.EXCLUDES = self.EXCLUDES
        event_handler.module_name = self.module_name

        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        while not self.stop_execution:
            try:
                time.sleep(0.1)
            except Exception as _:
                del _
