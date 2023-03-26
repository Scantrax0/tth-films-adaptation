from background_task import background
from player.models import VideoEntry
from processor.main import VideoProcessor
import json
import logging

@background()
def process_video(pk):

    print("starting task")
    instance = VideoEntry.objects.get(pk=pk)

    vp = VideoProcessor(instance.url)
    res = vp.analyze_brightness()
    print(res)
    if res.get('success'):
        instance.status = VideoEntry.SUCCESSFUL
        instance.brightness_data = json.dumps(res.get('data'))
    else:
        instance.status = VideoEntry.FAILED

    instance.save(update_fields=['status', 'brightness_data'])