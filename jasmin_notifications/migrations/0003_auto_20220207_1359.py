# Generated by Django 3.2.12 on 2022-02-07 13:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jasmin_notifications", "0002_auto_20210524_1418"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="notificationtype",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
