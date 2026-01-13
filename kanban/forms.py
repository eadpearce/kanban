from django import forms
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds import layout
from crispy_forms_gds.layout import Hidden

from kanban.models import Ticket, Board, BoardMembership, TicketStatus, User


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()


class BoardCreateForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        error_messages={
            "required": "Please enter a name",
        },
    )

    class Meta:
        model = Board
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML.h1("Create a new board"),
            "name",
            layout.Submit(
                "submit",
                "Create",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class BoardEditForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        error_messages={
            "required": "Please enter a name",
        },
    )

    class Meta:
        model = Board
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        board_id = kwargs.pop("board_id")
        super().__init__(*args, **kwargs)

        back_url = reverse_lazy("board-settings", kwargs={"pk": board_id})

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML(
                f'<a href="{back_url}" class="govuk-back-link">Back to board settings</a>'
            ),
            layout.HTML.h1("Edit board name"),
            "name",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class CreateMembershipForm(forms.ModelForm):
    user = UserChoiceField(label="User", queryset=User.objects.all())

    class Meta:
        model = BoardMembership
        fields = ("user",)

    def __init__(self, *args, **kwargs):
        self.board_id = kwargs.pop("board_id")
        super().__init__(*args, **kwargs)

        back_url = reverse_lazy(
            "board-manage-memberships", kwargs={"pk": self.board_id}
        )

        member_user_pks = BoardMembership.objects.filter(
            board_id=self.board_id
        ).values_list("pk")
        self.fields["user"].queryset = User.objects.exclude(
            pk__in=member_user_pks
        ).order_by("last_name")

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML(
                f'<a href="{back_url}" class="govuk-back-link">Back to manage memberships</a>'
            ),
            layout.HTML.h1("Add a member"),
            "user",
            layout.Submit(
                "submit",
                "Create",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class StatusCreateForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        error_messages={
            "required": "Please enter a name",
        },
    )

    class Meta:
        model = TicketStatus
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        board_id = kwargs.pop("board_id")
        super().__init__(*args, **kwargs)

        back_url = reverse_lazy("board-edit-columns", kwargs={"pk": board_id})

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML(
                f'<a href="{back_url}" class="govuk-back-link">Back to board columns</a>'
            ),
            layout.HTML.h1("Create a new column"),
            "name",
            layout.Submit(
                "submit",
                "Create",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class TicketCreateForm(forms.ModelForm):
    title = forms.CharField(
        label="Title",
        error_messages={
            "required": "Please enter a title",
        },
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(),
        error_messages={
            "required": "Please enter a description",
        },
    )
    status = forms.ModelChoiceField(
        label="Status",
        queryset=TicketStatus.objects.all(),
        required=False,
        help_text="Tickets with no assigned status will be added to the backlog",
    )

    class Meta:
        model = Ticket
        fields = ("title", "description")

    def __init__(self, *args, **kwargs):
        board_id = kwargs.pop("board_id")
        super().__init__(*args, **kwargs)

        self.fields["status"].queryset = TicketStatus.objects.filter(board__id=board_id)

        back_url = reverse_lazy("board-detail", kwargs={"pk": board_id})

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML(
                f'<a href="{back_url}" class="govuk-back-link">Back to board</a>'
            ),
            layout.HTML.h1("Create a new ticket"),
            "title",
            "description",
            "status",
            layout.Submit(
                "submit",
                "Create",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class TicketEditForm(forms.ModelForm):
    title = forms.CharField(
        label="Title",
        error_messages={
            "required": "Please enter a title",
        },
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(),
        error_messages={
            "required": "Please enter a description",
        },
    )
    status = forms.ModelChoiceField(
        label="Status",
        queryset=TicketStatus.objects.all(),
        required=False,
        help_text="Unassign status to move this ticket to the backlog",
    )

    class Meta:
        model = Ticket
        fields = ("title", "description")

    def __init__(self, *args, **kwargs):
        ticket_id = kwargs.pop("ticket_id")
        board_id = kwargs.pop("board_id")
        status_initial = kwargs.pop("status_initial")
        super().__init__(*args, **kwargs)

        self.fields["status"].queryset = TicketStatus.objects.filter(board__id=board_id)
        self.fields["status"].initial = status_initial

        back_url = reverse_lazy("ticket-detail", kwargs={"pk": ticket_id})

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML(
                f'<a href="{back_url}" class="govuk-back-link">Back to ticket</a>'
            ),
            layout.HTML.h1("Edit ticket"),
            "title",
            "description",
            "status",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class TicketAssigneeForm(forms.ModelForm):
    field_name = forms.CharField()
    assignee = UserChoiceField(
        label="",
        queryset=User.objects.all(),
        required=False,
    )

    class Meta:
        model = Ticket
        fields = ("assignee",)

    def __init__(self, *args, **kwargs):
        board_id = kwargs.pop("board_id")
        super().__init__(*args, **kwargs)

        member_user_pks = BoardMembership.objects.filter(board_id=board_id).values_list(
            "user__pk"
        )
        self.fields["assignee"].queryset = User.objects.filter(
            pk__in=member_user_pks
        ).order_by("last_name")

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            Hidden("field_name", value="assignee"),
            "assignee",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class TicketStatusForm(forms.ModelForm):
    field_name = forms.CharField()
    status = forms.ModelChoiceField(
        label="",
        queryset=TicketStatus.objects.all(),
        required=False,
    )

    class Meta:
        model = Ticket
        fields = ("status",)

    def __init__(self, *args, **kwargs):
        board_id = kwargs.pop("board_id")
        status_initial = kwargs.pop("status_initial")
        super().__init__(*args, **kwargs)

        self.fields["status"].queryset = TicketStatus.objects.filter(board__id=board_id)
        self.fields["status"].initial = status_initial
        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            Hidden("field_name", value="status"),
            "status",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class TicketTitleForm(forms.ModelForm):
    field_name = forms.CharField()
    title = forms.CharField(
        label="",
    )

    class Meta:
        model = Ticket
        fields = ("title",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            Hidden("field_name", value="title"),
            "title",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class TicketDescriptionForm(forms.ModelForm):
    field_name = forms.CharField()
    description = forms.CharField(
        label="",
        widget=forms.Textarea(),
    )

    class Meta:
        model = Ticket
        fields = ("description",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            Hidden("field_name", value="description"),
            "description",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )
