# Generated by Django 3.2.16 on 2023-05-05 14:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jasmin_notifications", "0003_auto_20220207_1359"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationtype",
            name="level",
            field=models.CharField(
                choices=[
                    ("info", "Info"),
                    ("attention", "Attention"),
                    ("success", "Success"),
                    ("warning", "Warning"),
                    ("error", "Error"),
                ],
                max_length=9,
            ),
        ),
    ]