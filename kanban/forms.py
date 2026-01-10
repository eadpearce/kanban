from django import forms
from django.urls import reverse_lazy

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds import layout

from kanban.models import Ticket, Board


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

    class Meta:
        model = Ticket
        fields = ("title", "description")

    def __init__(self, *args, **kwargs):
        board_id = kwargs.pop("board_id")
        super().__init__(*args, **kwargs)

        back_url = reverse_lazy("board-detail", kwargs={"pk": board_id})

        self.helper = FormHelper(self)
        self.helper.layout = layout.Layout(
            layout.HTML(
                f'<a href="{back_url}" class="govuk-back-link">Back to board</a>'
            ),
            layout.HTML.h1("Create a new ticket"),
            "title",
            "description",
            layout.Submit(
                "submit",
                "Create",
                data_module="govuk-button",
                data_prevent_double_click="true",
            ),
        )
