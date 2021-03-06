# Generated by Django 3.2.9 on 2021-12-14 11:09

from django.db import migrations


EVENT_TYPES = ((11, "DELETED", "The object was deleted"),)


def insert_event_types(apps, schema_editor):
    EventType = apps.get_model("event_log", "EventType")

    for pk, code, name in EVENT_TYPES:
        EventType.objects.create(pk=pk, code=code, name=name)


def delete_event_types(apps, schema_editor):
    EventType = apps.get_model("event_log", "EventType")

    for pk, _, _ in EVENT_TYPES:
        EventType.objects.get(pk=pk).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0040_merge_20211209_1432"),
    ]

    operations = [migrations.RunPython(insert_event_types, delete_event_types)]
