from pipeframe.core import PipelineEngine, PipeFrame
from io import BytesIO
from PIL import Image
import requests
import fcntl
import json


def clear_entry(entry):
    new_entry = {
        'title': entry['title'],
        'subreddit': entry['subreddit'],
        'thumbnail': entry['thumbnail']
     }
    return new_entry, True


def get_colors(entry):
    if entry['thumbnail'].startswith('http'):
        r = requests.get(entry['thumbnail'])
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content))
            w, h = img.size
            pixels = img.getcolors(w * h)
            entry['colors'] = pixels
            return entry, True
    return entry, False


def get_predominant_color(entry):
    biggest = (0, ())
    for pixel in entry['colors']:
        if pixel[0] > biggest[0]:
            biggest = pixel
    entry['predominant_color'] = biggest
    return entry, True


def write_to_disk(entry):
    """
    Clear the entry, lock the file, write entry, unlock the file.
    """
    del entry['colors']
    del entry['title']
    del entry['thumbnail']

    with open("log", "a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.write(json.dumps(entry)+'\n')
        fcntl.flock(fh, fcntl.LOCK_UN)

    return entry, True


class RedditDataPipeline(PipelineEngine):
    steps = [clear_entry, get_colors, get_predominant_color, write_to_disk]
    load = 'stream'

    @staticmethod
    def feed(bucket):
        req = requests.get('https://www.reddit.com/r/all/top.json', headers={'User-agent': 'pipeframe'})
        if req.status_code == 200:
            data = req.json()['data']['children']
            for entry in data:
                bucket.put(entry['data'])


pipe_frame = PipeFrame(_cpu_count=8, stream_buffer_size=50000)
pipe_frame.run(RedditDataPipeline)

