from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


User = get_user_model()


class EventType(models.Model):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        return self.name


class Event(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    event_type = models.ForeignKey(
        EventType,
        models.CASCADE,
        related_name="+",
    )
    user = models.ForeignKey(
        User,
        models.SET_NULL,
        null=True,
        related_name="event_log",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=254)

    def __str__(self) -> str:
        return f"{self.event_type.name}: {self.description}"
