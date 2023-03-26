from django.db.models.signals import pre_save

from player.models import VideoEntry
from processor.main import VideoProcessor


def video_entry_pre_save_handler(*args, **kwargs):
    instance = kwargs.get('instance')

    print(instance.url)
    vp = VideoProcessor(instance.url)
    res = vp.analyze_brightness()
    print(res)

    if res:
        instance.status = VideoEntry.SUCCESSFUL
        instance.brightness_data = res
    else:
        instance.status = VideoEntry.FAILED


pre_save.connect(receiver=video_entry_pre_save_handler, sender=VideoEntry)
