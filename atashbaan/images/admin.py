from django.contrib import admin

from .models import Image


# Register your models here.
class ImageAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "image",
        "tag",
        "user",
        "created_at",
        "last_modified",
    ]
    ordering = [
        "created_at",
    ]


admin.site.register(Image, ImageAdmin)
