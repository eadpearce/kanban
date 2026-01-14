from django import forms
from django.urls import reverse_lazy

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds import layout
from crispy_forms_gds.layout import Hidden

from kanban.models import (
    Ticket,
    Board,
    BoardMembership,
    TicketStatus,
    Sprint,
    User,
    Comment,
)


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


class SprintCreateForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        error_messages={
            "required": "Please enter a name",
        },
    )

    class Meta:
        model = Sprint
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML.h1("Create a new sprint"),
            layout.HTML.p(
                "Once created your sprint will be visible in the backlog of your board where you will be able to add tickets to it"
            ),
            "name",
            layout.Submit(
                "submit",
                "Create",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class SprintCompleteForm(forms.Form):

    def __init__(self, *args, **kwargs):
        board = kwargs.pop("board")
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML.h1("Complete this sprint"),
            layout.HTML.p(
                "Once the sprint is completed any tickets that do not have a status of “Done” will be moved back to the backlog."
            ),
            layout.Submit(
                "submit",
                "Complete sprint",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class SprintStartForm(forms.Form):

    def __init__(self, *args, **kwargs):
        board = kwargs.pop("board")
        super().__init__(*args, **kwargs)

        active_sprint_warning = ""
        if board.active_sprint:
            active_sprint_warning = layout.HTML.warning(
                "This board already has an active sprint. Starting a new sprint will move the current active sprint back into the backlog."
            )

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML.h1("Start this sprint"),
            active_sprint_warning,
            layout.HTML.p(
                "Once the sprint is started, its tickets will be moved to the board. Any tickets already in the board will be moved to the backlog."
            ),
            layout.Submit(
                "submit",
                "Start sprint",
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
        required=False,
    )
    sprint = forms.ModelChoiceField(
        label="Sprint",
        queryset=Sprint.objects.all(),
        required=False,
    )

    class Meta:
        model = Ticket
        fields = ("title", "description")

    def __init__(self, *args, **kwargs):
        board_id = kwargs.pop("board_id")
        sprint_id = kwargs.pop("sprint_id")
        super().__init__(*args, **kwargs)

        self.fields["sprint"].queryset = Sprint.objects.filter(
            completed_date__isnull=True
        )

        if sprint_id and sprint_id != "backlog":
            sprint = Sprint.objects.get(pk=sprint_id)
            self.fields["sprint"].initial = sprint

        back_url = reverse_lazy("board-detail", kwargs={"pk": board_id})

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML(
                f'<a href="{back_url}" class="govuk-back-link">Back to board</a>'
            ),
            layout.HTML.h1("Create a new ticket"),
            "title",
            "description",
            "sprint",
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
    form_name = forms.CharField()
    assignee = UserChoiceField(
        label="",
        queryset=User.objects.all(),
        required=False,
        empty_label="Unassigned",
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
            Hidden("form_name", value="assignee"),
            "assignee",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class TicketStatusForm(forms.ModelForm):
    form_name = forms.CharField()
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
            Hidden("form_name", value="status"),
            "status",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class TicketTitleForm(forms.ModelForm):
    form_name = forms.CharField()
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
            Hidden("form_name", value="title"),
            "title",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class TicketDescriptionForm(forms.ModelForm):
    form_name = forms.CharField()
    description = forms.CharField(
        label="",
        widget=forms.Textarea(),
        required=False,
    )

    class Meta:
        model = Ticket
        fields = ("description",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            Hidden("form_name", value="description"),
            "description",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class StatusEditForm(forms.ModelForm):
    name = forms.CharField(label="")

    class Meta:
        model = TicketStatus
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML.h1("Rename ticket"),
            "name",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )


class CommentCreateForm(forms.ModelForm):
    form_name = forms.CharField()
    text = forms.CharField(
        label="",
        widget=forms.Textarea(),
        error_messages={
            "required": "Comment text cannot be blank",
        },
    )

    class Meta:
        model = Comment
        fields = ("text",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            Hidden("form_name", value="comment"),
            "text",
            layout.Submit(
                "submit",
                "Save",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )
