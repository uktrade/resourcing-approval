from enum import Enum, unique
from typing import Any, Optional

from django.db import models

import event_log.models as event_log_models
from user.models import User


@unique
class EventType(Enum):
    """Enum class for event types in the application.

    Key:
        Each key must match a code in the event type table.

    Value:
        tuple[string, Optional[set[str]]]

        The first string is the event description. The second optional set of strings
        are the context kwargs required for the description string to be formatted.
    """

    # value = tuple[string, Optional[set[str]]]
    CREATED = ("Created a {object}", {"object"})
    UPDATED = ("Updated a {object}", {"object"})
    SENT_FOR_APPROVAL = ("Sent the resourcing request for approval", None)
    AMENDING = ("Amending the resourcing request", None)
    SENT_FOR_REVIEW = ("Sent the amendments for review", None)
    REVIEWED_AMENDMENTS = ("Reviewed the amendments", None)
    GROUP_APPROVED = ("{group} approved the resourcing request", {"group"})
    GROUP_REJECTED = ("{group} rejected the resourcing request", {"group"})
    COMMENTED = ("Commented on the resourcing request", None)
    APPROVED = ("The resourcing request was approved", None)
    DELETED = ("Deleted a {object}", {"object"})
    COMPLETED = ("Marked the resourcing request as complete", None)


class EventLogService:
    @classmethod
    def add_event(
        cls,
        content_object: models.Model,
        user: User,
        event_type: EventType,
        event_context: Optional[dict[str, Any]] = None,
    ) -> event_log_models.Event:
        """Add an event that happened in the application to the event log.

        Args:
            content_object: The related instance. So far this is always a ResourcingRequest instance.
            user: The user who triggered the event.
            event_type: What type of event happened.
            event_context: Context required for the event description. Defaults to None.

        Raises:
            ValueError: If the event_context is not correct.

        Returns:
            The newly created event.
        """

        if event_context is None:
            event_context = {}

        code = event_type.name
        message, event_context_kwargs = event_type.value

        if event_context_kwargs:
            if event_context_kwargs != set(event_context):
                raise ValueError("Invalid event_context")

            message = message.format(**event_context)

        event = event_log_models.Event.objects.create(
            content_object=content_object,
            event_type=event_log_models.EventType.objects.get(code=code),
            user=user,
            description=message,
        )

        return event


class EventLogMixin:
    """A view mixin that logs an event if the view request is successful.

    This mixin patches django's form views to check if they were successful/had changes.

    The `event_type` attribute and the `get_event_content_object` method are the minimum
    required things you will need to implement to use this mixin.

    Example:
        class SomeView(EventLogMixin, CreateView):
            model = SomeModel
            form_class = SomeForm
            event_type = EventType.CREATED

            def get_event_content_object(self) -> models.Model:
                return self.object
    """

    event_methods: list[str] = ["post"]
    event_type: EventType
    event_context: Optional[dict[str, Any]] = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.event_success = True

    def form_invalid(self, form):
        self.event_success = False

        return super().form_invalid(form)

    def form_valid(self, form):
        if not form.has_changed():
            self.event_success = False

        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if request.method.lower() not in self.event_methods:
            return response

        if not self.event_success:
            return response

        event_type = self.get_event_type()

        if not event_type:
            return response

        EventLogService.add_event(
            content_object=self.get_event_content_object(),
            user=request.user,
            event_type=event_type,
            event_context=self.get_event_context(),
        )

        return response

    def get_event_content_object(self) -> models.Model:
        raise NotImplementedError

    def get_event_type(self) -> EventType:
        return self.event_type

    def get_event_context(self) -> Optional[dict[str, Any]]:
        return self.event_context
