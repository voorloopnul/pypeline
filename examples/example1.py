from pipeframe.core import PipelineEngine, PipeFrame
import fcntl
import json


def clear_entry(entry):
    entry['new_number'] = 0
    return entry, True


def power(entry):
    entry['new_number'] = entry['number'] ** entry['number']
    return entry, True


def write_to_disk(entry):
    """
    Lock the file, write entry, release the file.
    """
    with open("log", "a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.write(json.dumps(entry['number'])+'\n')
        fcntl.flock(fh, fcntl.LOCK_UN)

    return entry, True


class RedditDataPipeline(PipelineEngine):
    steps = [clear_entry, power, write_to_disk]
    source = 'batch'

    @staticmethod
    def feed(bucket):
        x = 1000000
        for i in range(10):
            x += 1000
            entry = {'number': x}
            bucket.put(entry)


# With all cpu  - 1
pipe_frame = PipeFrame()
pipe_frame.run(RedditDataPipeline)


# With 2 cpus
pipe_frame = PipeFrame(cpu_count=2)
pipe_frame.run(RedditDataPipeline)
