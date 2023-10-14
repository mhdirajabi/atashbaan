import datetime
import posixpath

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

import pytz

User = get_user_model()


def user_uploads_path(instance, filename):
    date = datetime.datetime.now(tz=pytz.timezone("Asia/Tehran"))
    year = date.year
    month = date.month
    day = date.day

    dirname = f"images/{instance.user.id}/{instance.tag}/{year}/{month}/{day}/"

    return posixpath.join(dirname, filename)


class UnprocessedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(tag="unprocessed")


class ProcessedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(tag="processed")


class Image(models.Model):
    TAG_CHOICES = (("processed", "پردازش شده"), ("unprocessed", "پردازش نشده"))

    image = models.ImageField(
        "تصویر", upload_to=user_uploads_path, blank=False, null=False
    )
    tag = models.CharField(
        "برچسب", max_length=20, default="unprocessed", choices=TAG_CHOICES
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="images", verbose_name="کاربر"
    )

    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    last_modified = models.DateTimeField("آخرین بروزرسانی", auto_now=True)

    objects = models.Manager()
    unprocessed = UnprocessedManager()
    processed = ProcessedManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["image"],
                condition=Q(tag="processed"),
                name="unique_processed_image",
            )
        ]
        ordering = [
            "created_at",
        ]
