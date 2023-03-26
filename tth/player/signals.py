from django.db.models.signals import post_save
from django.dispatch import receiver
from player.tasks import process_video

from player.models import VideoEntry
import logging

logger = logging.getLogger("django")

@receiver(post_save, sender=VideoEntry)
def process_video_start(sender, instance, **kwargs):
    update_fields = kwargs.get('update_fields', None)
    if update_fields or instance.status == 'S':
        return
    process_video(instance.pk)
    
    

# def video_entry_pre_save_handler(*args, **kwargs):
#     instance = kwargs.get('instance')

#     print(instance.url)
#     vp = VideoProcessor(instance.url)
#     res = vp.analyze_brightness()
#     print(res)

#     if res.get('success'):
#         instance.status = VideoEntry.SUCCESSFUL
#         instance.brightness_data = res
#     else:
#         instance.status = VideoEntry.FAILED


# pre_save.connect(receiver=video_entry_pre_save_handler, sender=VideoEntry)
