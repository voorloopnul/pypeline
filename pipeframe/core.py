import time
from multiprocessing import Process, Queue, cpu_count as _cpu_count
from queue import Empty


class PipelineEngine(Process):
    steps = []
    timeout = 2
    source = 'batch'

    def __init__(self, name, input_queue, output_queue):
        super(PipelineEngine, self).__init__()
        self.name = name
        self.input_queue = input_queue
        self.output_queue = output_queue

    def run(self):
        print("Starting worker {0}".format(self.name))
        count = 0
        while True:
            try:
                entry = self.input_queue.get(timeout=self.timeout)
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

    def __init__(self, cpu_count=_cpu_count()-1, buffer_size=10000):
        self.input_queue = Queue(buffer_size)
        self.output_queue = Queue()
        self.cpu_count = cpu_count

    def run(self, _pipeline, load=None):
        start_time = time.time()
        load_function = load if load else _pipeline.feed

        if _pipeline.source == 'batch':
            load_function(self.input_queue)

        worker_list = []
        for i in range(self.cpu_count):
            worker = _pipeline(name="worker-{0}".format(i), input_queue=self.input_queue, output_queue=self.output_queue)
            worker_list.append(worker)

        [worker.start() for worker in worker_list]

        if _pipeline.source == 'stream':
            load_function(self.input_queue)

        [worker.join() for worker in worker_list]

        print("Done!")
        self.input_queue.cancel_join_thread()
        end_time = time.time()
        print("Elapsed time: {0}s".format(round(end_time-start_time, 2)))
