import time
from multiprocessing import Process, Queue, cpu_count
from queue import Empty


class PipelineEngine(Process):
    steps = []
    timeout = 2
    source = 'batch'

    def __init__(self, name, stream, output):
        super(PipelineEngine, self).__init__()
        self.name = name
        self.stream = stream
        self.output = output

    def run(self):
        count = 0
        while True:
            try:
                entry = self.stream.get(timeout=self.timeout)
                for step in self.steps:
                    entry, keep_processing = step(entry)
                    if not keep_processing:
                        break
                count += 1
            except Empty:
                # the "infinity" stream has dried
                break
        print("Finished {0} with {1} entries".format(self.name, count))

    @staticmethod
    def feed(bucket):
        pass


class PipeFrame(object):

    def __init__(self, _cpu_count=cpu_count()-1, stream_buffer_size=1000):
        self.stream = Queue(stream_buffer_size)
        self.output = Queue()
        self.cpu_count = _cpu_count

    def run(self, _pipeline, load=None):
        start_time = time.time()
        load_function = load if load else _pipeline.feed

        if _pipeline.source == 'batch':
            load_function(self.stream)

        worker_list = []
        for i in range(self.cpu_count):
            worker = _pipeline(name="worker-{0}".format(i), stream=self.stream, output=self.output)
            worker_list.append(worker)

        [worker.start() for worker in worker_list]

        if _pipeline.source == 'stream':
            load_function(self.stream)

        print("Waiting to join...")
        [worker.join() for worker in worker_list]

        print("Done!")
        self.stream.cancel_join_thread()
        end_time = time.time()
        print("Elapsed time: {0}s".format(round(end_time-start_time, 2)))
