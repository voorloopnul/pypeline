# PipeFrame Documentation

PipeFrame is a small library to help you process data (stream or batch) taking advantage of python multiprocessing library.

## Installation

Pipeframe in available at pip, to install it in your environment just do:

 > pip install pipeframe

## Getting started

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

Your functions should receive as parameter the record to be processed and return
the modified record and a boolean that is used to bypass further steps execution
on the data (False) or keep going with the pipeline flow (True).

```python3
def func1(record):
    if record.is_upper():
        return record, False
    else:
        return record.lower(), True 
```

You also have to provide a function `feed´ to feed your process with some data:

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



To execute your newly created pipeline you must call it using PipeFrame:

```python3
from pipeframe.core import PipeFrame
pipe_frame = PipeFrame(cpu_count=16, stream_buffer_size=50000)
pipe_frame.run(YourCustomPipeline)
```

The `cpu_count` and `stream_buffer_size` are optional arguments:

 - cpu_count: an integer that defaults to the number o cores in your machine minus 1
 - stream_buffer_size: an integer that defaults to 1000
 
 ## Stream or Batch?
 
 By default your pipeline will run in batch mode, it means that your feed function will run and complete before the step
 functions start. You have to be aware of how much data entries are going to the queue and tune the stream_buffer_size according
 to that.
 
 If you make source='stream' your feed function will start after the step functions and the feeding and processing
 will happen in parallel. In that case you should tune the timeout attribute for a value high enough to prevent the
 pipeline termination due absence of data in the queue. 
 
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
