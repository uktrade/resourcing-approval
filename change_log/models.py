from collections import ChainMap

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.db.models.signals import pre_save

from change_log.utils import get_instance_value


class ChangeQuerySet(models.QuerySet):
    def get_changes(self):
        return ChainMap(
            *self.all().order_by("-timestamp").values_list("changes", flat=True)
        )


class Change(models.Model):
    class Meta:
        ordering = ["-timestamp"]
        get_latest_by = "timestamp"

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(encoder=DjangoJSONEncoder)

    objects = ChangeQuerySet.as_manager()


class ChangeLogRelation(GenericRelation):
    # Django provides this method as a hook for modifying the model class.
    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)

        pre_save.connect(self.pre_save, sender=cls, weak=False)

    def pre_save(self, sender, instance, **kwargs):
        is_new = instance._state.adding

        if is_new:
            return

        prev_instance = sender.objects.get(pk=instance.pk)

        changes = {}

        for field in instance._meta.get_fields():
            prev_value = get_instance_value(prev_instance, field)
            next_value = get_instance_value(instance, field)

            if prev_value != next_value:
                changes[field.name] = prev_value

        def add_change():
            change = Change.objects.create(
                content_object=instance,
                changes=changes,
            )
            getattr(instance, self.name).add(change)

        transaction.on_commit(add_change)
