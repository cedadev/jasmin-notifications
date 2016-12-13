# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-13 17:21
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import jasmin_django_utils.enumfield
import jasmin_notifications.models
import picklefield.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('target_id', models.CharField(max_length=250)),
                ('link', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('followed_at', models.DateTimeField(blank=True, null=True)),
                ('extra_context', picklefield.fields.PickledObjectField(default={}, editable=False)),
            ],
            options={
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='NotificationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='A short name for the notification', max_length=50, validators=[django.core.validators.RegexValidator(regex='^[a-zA-Z0-9_-]+$')])),
                ('level', jasmin_django_utils.enumfield.EnumField(jasmin_notifications.models.NotificationLevel)),
                ('display', models.BooleanField(default=True, help_text='Indicates of notifications of this type should be displayed on site as well as emailed (user notifications only)')),
            ],
        ),
        migrations.CreateModel(
            name='EmailNotification',
            fields=[
                ('notification_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_notifications.Notification')),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
                'abstract': False,
            },
            bases=('jasmin_notifications.notification',),
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('notification_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_notifications.Notification')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('jasmin_notifications.notification',),
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jasmin_notifications.NotificationType'),
        ),
        migrations.AddField(
            model_name='notification',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_jasmin_notifications.notification_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='notification',
            name='target_ctype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
    ]
