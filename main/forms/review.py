from django import forms

from main.models import Approval
from main.services.review import ReviewAction
from main.utils import get_user_related_approval_types


class ReviewForm(forms.Form):
    approval_type = forms.TypedChoiceField(
        choices=Approval.Type.choices,
        coerce=Approval.Type,
        required=False,
        empty_value=None,
    )
    text = forms.CharField(
        label="Add a comment, ask for more information or request a change",
        required=False,
        empty_value=None,
        widget=forms.Textarea(attrs={"rows": 5}),
    )
    action = forms.TypedChoiceField(
        choices=[(x.value, x.value) for x in ReviewAction],
        coerce=ReviewAction,
    )

    def __init__(self, *args, user, resourcing_request, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user
        self.resourcing_request = resourcing_request

        self.fields["approval_type"].choices = [
            (approval_type.value, approval_type.label)
            for approval_type in get_user_related_approval_types(
                user, resourcing_request
            )
        ]

    def clean(self):
        # The validation here covers potential user errors that should not result in a
        # 500/stack trace.
        cleaned_data = super().clean()

        action = cleaned_data.get("action")
        approval_type = cleaned_data.get("approval_type")
        text = cleaned_data.get("text")

        if action == ReviewAction.APPROVE:
            if not approval_type:
                self.add_error(
                    "approval_type", "This field is required when approving."
                )

            if (
                approval_type == Approval.Type.CHIEF
                and self.user != self.resourcing_request.chief
                and not self.user.is_superuser
            ):
                self.add_error(
                    None, "Only the nominated Chief can give Chief approval."
                )

            if (
                approval_type == Approval.Type.HEAD_OF_PROFESSION
                and self.user.profession != self.resourcing_request.profession
                and not self.user.is_superuser
            ):
                self.add_error(
                    None,
                    "Only the relevant Head of Profession can give Head of Profession approval.",
                )

        if action in (
            ReviewAction.CLEAR_APPROVAL,
            ReviewAction.REQUEST_CHANGES,
            ReviewAction.COMMENT,
        ):
            if not text:
                self.add_error(
                    "text",
                    (
                        "This field is required when clearing an approval, requesting"
                        " changes or adding a comment."
                    ),
                )
