# Generated by Django 4.2.4 on 2023-08-27 17:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("images", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="image",
            options={"ordering": ["created_at"]},
        ),
        migrations.AddField(
            model_name="image",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now, verbose_name="تاریخ ایجاد"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="image",
            name="last_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی"),
        ),
        migrations.AddField(
            model_name="image",
            name="tag",
            field=models.CharField(
                choices=[("processed", "پردازش شده"), ("unprocessed", "پردازش نشده")],
                default="unprocessed",
                max_length=20,
                verbose_name="برچسب",
            ),
        ),
    ]
