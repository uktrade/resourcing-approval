import pytest

import event_log.models as event_log_models
from event_log.models import Event
from main.services.event_log import EventLogService, EventType


def test_event_type_enum_in_sync_with_migrations(db):
    assert set(x.name for x in EventType) == set(
        event_log_models.EventType.objects.values_list("code", flat=True)
    )


def test_add_event(db, resourcing_request, admin_user):
    prev_count = Event.objects.count()

    EventLogService.add_event(
        resourcing_request,
        admin_user,
        EventType.GROUP_APPROVED,
        {"group": "HRBP"},
    )

    assert Event.objects.count() == prev_count + 1


def test_add_event_invalid_message_context(db, resourcing_request, admin_user):
    with pytest.raises(ValueError):
        EventLogService.add_event(
            resourcing_request,
            admin_user,
            EventType.GROUP_APPROVED,
        )
