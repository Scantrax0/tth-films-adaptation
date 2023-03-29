from background_task import background
from player.models import VideoEntry
from processor.main import VideoProcessor
import json
import logging

@background()
def process_video(pk):

    print("starting task")
    instance = VideoEntry.objects.get(pk=pk)

    vp = VideoProcessor('youtube', instance.url)
    res = vp.analyze_brightness()
    print(res)
    if res.get('success'):
        instance.status = VideoEntry.SUCCESSFUL
        instance.brightness_data = json.dumps(res.get('data'))
        instance.dangerous_interval = json.dumps(res.get('danger_intervals'))
    else:
        instance.status = VideoEntry.FAILED

    instance.save(update_fields=['status', 'brightness_data', 'dangerous_interval'])
