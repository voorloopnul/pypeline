# PipeFrame
What is a Pipeline? 

> In computing, a pipeline, also known as a data pipeline, is a set of data processing elements connected in series, where the output of one element is the input of the next one. The elements of a pipeline are often executed in parallel or in time-sliced fashion. Some amount of buffer storage is often inserted between elements.

_source: Wikipedia_

PipeFrame is a small **pipe**line **frame**work that help you process data (stream or batch) taking advantage of python multiprocessing library.

## Installation

The package in available at pip, to install it in your environment just do:

 > pip install pipeframe

## Getting started

### Create your pipeline
The first thing you should do is create your pipeline, it should inherited from `pipeframe.core.PipelineEngine`
and include a `steps` class attribute:

```python3
from pipeframe.core import PipelineEngine
class YourCustomPipeline(PipelineEngine):
    steps = [func1, func2, ...]
```

The pipeline will execute each entry against the `steps` functions. You can 
define any amount of functions to perform on your data, the execution order
will follow the same order you defined in the steps list.

Your function should receive as parameter the record to be processed and return
the modified record and a boolean that is used to bypass further steps execution
on the data (False) or keep going with the pipeline flow (True).

```python3
def func1(record):
    if record.is_upper():
        return record, False
    else:
        return record.lower(), True 
```

You also have to provide a function named `feed` that will feed your process with some data:

```python3
class YourCustomPipeline(PipelineEngine):
    steps = [func1, func2, ...]

    def feed(self, bucket):
        req = requests.get('https://www.reddit.com/r/all/top.json', headers={'User-agent': 'pipeframe'})
        if req.status_code == 200:
            data = req.json()['data']['children']
            for entry in data:
                bucket.put(entry['data'])
```

### Run your pipeline

To execute your newly created pipeline you must call it using PipeFrame executor:

```python3
from pipeframe.core import PipeFrame
pipe_frame = PipeFrame(cpu_count=16, buffer_size=50000)
pipe_frame.run(YourCustomPipeline)
```

The `cpu_count` and `buffer_size` are optional arguments:

 - cpu_count: an integer that defaults to the number of cores in your machine minus 1
 - buffer_size: an integer that defaults to 10000 
 
 ## Stream or Batch?
 
 By default your pipeline will run in batch mode, it means that **your feed function will run and complete before the step
 functions start**. You have to be aware of how much data entries are going to the queue and tune the _buffer_size_ 
 according to that.
 
 If you make _source='stream'_ **your feed function will start after the step functions and the feeding and processing
 will happen in parallel**. In that case you should tune the timeout attribute for a value high enough to prevent the
 pipeline termination due temporary absence of data in the queue ( For the cases that you data ingestion is slower than 
 your capacity to process it). 
 
 Example:
 
 ```python3
class YourCustomPipeline(PipelineEngine):
    steps = [func1, func2, ...]
    source = 'stream'
    timeout = 10 

    def feed(self, bucket):
        for entry in infinite_stream_of_data():
            bucket.put(entry)
```

In the example above your workers will wait up to 10 seconds for the the infinite_stream_of_data() function to produce 
new data to be processed, if no new data arrive in 10 seconds, the workers will terminated because your stream has dried.

## Full example

```python 
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


class PowerDataPipeline(PipelineEngine):
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
pipe_frame.run(PowerDataPipeline)


# With 2 cpus
pipe_frame = PipeFrame(cpu_count=2)
pipe_frame.run(PowerDataPipeline)
```
