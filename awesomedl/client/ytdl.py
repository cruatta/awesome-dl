from youtube_dl import YoutubeDL
from awesomedl import *
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread
import time
from typing import *


class YTDL(object):

    dl_queue = Queue()
    ytdl_pool = ThreadPoolExecutor(2)
    ytdl = YoutubeDL()

    def __init__(self):
        dl_thread = Thread(target=self.__yt_download)
        dl_thread.start()

    def __yt_download(self):
        while True:
            time.sleep(1)
            task = self.dl_queue.get()
            future = self.ytdl_pool.submit(self.ytdl.download, [task.url])
            self.dl_queue.task_done()


    def add(self, task: DownloadTask):
        self.dl_queue.put(task)

    def tasks(self) -> List[DownloadTask]:
        return list(self.dl_queue.queue)

