from django.db import models


class VideoEntry(models.Model):
    LOADED = 'L'
    SUCCESSFUL = 'S'
    FAILED = 'F'
    STATUSES = [
        (LOADED, 'Загружено'),
        (SUCCESSFUL, 'Обработано'),
        (FAILED, 'Ошибка'),
    ]

    url = models.URLField('URL', unique=True, db_index=True)
    status = models.CharField('Статус', max_length=40, choices=STATUSES,
                              default=LOADED)
    brightness_data = models.TextField('Данные яркости', blank=True, null=True, default="null")

    class Meta:
        verbose_name = 'Видео'
        verbose_name_plural = 'Видео'

    def __str__(self):
        return f'{self.status} | {self.url}'
