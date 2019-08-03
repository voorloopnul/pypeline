# PipeFrame Documentation

PipeFrame is a small library to help you process data (stream or batch) taking advantage of python multiprocessing library.


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
will follow the same order you defined on the list.

Your functions should receive as parameter the record to be processed and return
the modified record and a boolean that is used to bypass further steps execution
on the data (False) or keep going with the pipeline flow (True).

```python3
def func1(record):
    if record.is_upper():
        return record, False
    else:
        return record.lower(), True 
    
def func2(record):
    return record.capitalize(), True 
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
 
If you have multiple pipelines you can also run them in series:

```
pipe_frame = PipeFrame()
pipe_frame.run(Pipeline01).run(Pipeline02)
```


  

me
