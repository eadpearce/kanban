import json
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import (
    DetailView,
    View,
    FormView,
    ListView,
    UpdateView,
    TemplateView,
)
from django.http import JsonResponse
from kanban.models import Board, BoardMembership, Ticket, TicketStatus, User
from kanban import forms
from kanban.constants import BasicStatuses


class CreateBoardView(FormView):
    form_class = forms.BoardCreateForm
    template_name = "core/form.html"

    def get_success_url(self, board_id):
        return redirect(reverse("board-detail", kwargs={"pk": board_id}))

    def form_valid(self, form):
        data = form.cleaned_data
        board = Board.objects.create(
            name=data["name"],
        )
        # create basic statuses by default
        for i, name in enumerate(BasicStatuses.values):
            TicketStatus.objects.create(name=name, board=board, order=i)

        BoardMembership.objects.create(
            board=board, user=self.request.user, is_owner=True
        )

        return self.get_success_url(board.id)


class EditBoardView(UpdateView):
    form_class = forms.BoardEditForm
    template_name = "core/form.html"
    queryset = Board.objects.all()

    def get_success_url(self, board_id):
        return redirect(reverse("board-detail", kwargs={"pk": board_id}))

    def form_valid(self, form):
        data = form.cleaned_data
        self.object.name = data["name"]
        self.object.save()
        return self.get_success_url(self.object.id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board_id"] = self.kwargs.get("pk")
        return kwargs


class BoardView(DetailView):
    template_name = "kanban/board.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = self.object.statuses.all().order_by("order")
        is_member = BoardMembership.objects.filter(
            board=self.object, user=self.request.user
        ).exists()
        context["is_member"] = is_member
        if is_member:
            context["is_owner"] = BoardMembership.objects.get(
                board=self.object, user=self.request.user
            ).is_owner
        else:
            context["is_owner"] = False
        return context


class BoardSettingsView(DetailView):
    template_name = "kanban/board_settings.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = self.object.statuses.all().order_by("order")
        context["owner"] = self.object.members.filter(is_owner=True).first().user
        return context


class BoardEditColumnsView(DetailView):
    template_name = "kanban/board_edit_columns.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = self.object.statuses.all().order_by("order")
        return context

    def post(self, request, *args, **kwargs):
        selected_statuses = request.POST.getlist("selected_status")
        action = request.POST.get("form-action")
        if action == "delete":
            statuses = TicketStatus.objects.filter(id__in=selected_statuses)
            column_names = ", ".join([f"“{status.name}”" for status in statuses])
            tickets = Ticket.objects.filter(status__id__in=statuses)
            tickets.update(status=None)
            for ticket in tickets:
                ticket.save()
            statuses.delete()
            messages.success(
                request,
                f"Column(s) {column_names} deleted. Any associated tickets have been moved to the backlog",
            )
        board = Board.objects.get(pk=self.kwargs["pk"])
        return redirect(reverse("board-edit-columns", kwargs={"pk": board.pk}))


class BacklogView(ListView):
    template_name = "kanban/backlog.html"
    model = Ticket

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(board__id=self.kwargs["pk"], status__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = Board.objects.get(pk=self.kwargs["pk"])
        context["board"] = board
        context["statuses"] = board.statuses.all().order_by("order")
        context["is_member"] = BoardMembership.objects.filter(
            board=board, user=self.request.user
        ).exists()
        return context

    def post(self, request, *args, **kwargs):
        selected_tickets = request.POST.getlist("selected_tickets")
        action = request.POST.get("form-action")
        tickets = Ticket.objects.filter(id__in=selected_tickets)
        ticket_titles = ", ".join([f"“{ticket.title}”" for ticket in tickets])

        if action == "delete":
            tickets.delete()
            messages.success(
                request,
                f"Ticket(s) {ticket_titles} deleted",
            )
        elif action == "update-status":
            status_id = request.POST.get("status")
            status = TicketStatus.objects.get(id=status_id)
            for ticket in tickets:
                ticket.status = status
                ticket.save()
            messages.success(
                request,
                f"Ticket(s) {ticket_titles} moved to “{status.name}”",
            )
        return self.get(request)


class TicketView(TemplateView):
    template_name = "kanban/ticket.html"

    FORM_MAPPING = {
        "assignee": forms.TicketAssigneeForm,
        "status": forms.TicketStatusForm,
        "description": forms.TicketDescriptionForm,
    }

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        data = request.POST
        obj = Ticket.objects.get(pk=self.kwargs["pk"])

        if data["field_name"] == "assignee":
            form = forms.TicketAssigneeForm(data=data, instance=obj)
            if not form.is_valid():
                return self.form_invalid(form)
            obj.assignee = User.objects.get(id=data["assignee"])

        if data["field_name"] == "status":
            form = forms.TicketStatusForm(
                data=data,
                instance=obj,
                board_id=obj.board.id,
                status_initial=obj.status,
            )
            if not form.is_valid():
                return self.form_invalid(form)
            obj.status = TicketStatus.objects.get(id=data["status"])

        if data["field_name"] == "description":
            form = forms.TicketDescriptionForm(instance=obj, data=data)
            if not form.is_valid():
                return self.form_invalid(form)
            obj.description = data["description"]

        obj.save()
        print(obj.__dict__)
        return redirect(reverse("ticket-detail", kwargs={"pk": obj.pk}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = Ticket.objects.get(pk=self.kwargs["pk"])
        context["object"] = obj
        context["users"] = User.objects.all()
        context["assignee_form"] = forms.TicketAssigneeForm(instance=obj)
        context["status_form"] = forms.TicketStatusForm(
            instance=obj,
            board_id=obj.board.id,
            status_initial=obj.status,
        )
        context["description_form"] = forms.TicketDescriptionForm(instance=obj)
        context["fields"] = json.dumps(["assignee", "status", "description"])
        is_member = BoardMembership.objects.filter(
            board=obj.board, user=self.request.user
        ).exists()
        context["is_member"] = is_member
        return context


class CreateTicketView(FormView):
    form_class = forms.TicketCreateForm
    template_name = "core/form.html"

    def get_success_url(self, board_id):
        return redirect(reverse("board-detail", kwargs={"pk": board_id}))

    def form_valid(self, form):
        data = form.cleaned_data
        board = Board.objects.get(pk=self.kwargs.get("pk"))
        Ticket.objects.create(
            title=data["title"],
            description=data["description"],
            status=data["status"],
            board=board,
            author=self.request.user,
        )
        return self.get_success_url(board.id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board_id"] = self.kwargs.get("pk")
        return kwargs


class CreateStatusView(FormView):
    form_class = forms.StatusCreateForm
    template_name = "core/form.html"

    def get_success_url(self, board_id):
        return redirect(reverse("board-edit-columns", kwargs={"pk": board_id}))

    def form_valid(self, form):
        data = form.cleaned_data
        board = Board.objects.get(pk=self.kwargs.get("pk"))
        TicketStatus.objects.create(
            name=data["name"],
            board=board,
        )
        return self.get_success_url(board.id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board_id"] = self.kwargs.get("pk")
        return kwargs


class EditTicketView(UpdateView):
    form_class = forms.TicketEditForm
    template_name = "core/form.html"
    queryset = Ticket.objects.all()

    def get_success_url(self):
        return redirect(reverse("ticket-detail", kwargs={"pk": self.object.id}))

    def form_valid(self, form):
        data = form.cleaned_data
        self.object.title = data["title"]
        self.object.description = data["description"]
        self.object.status = data["status"]
        self.object.save()
        return self.get_success_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["ticket_id"] = self.object.id
        kwargs["board_id"] = self.object.board.id
        kwargs["status_initial"] = self.object.status
        return kwargs


class UpdateTicketStatusAJAXView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        ticket = Ticket.objects.get(id=data.get("id"))
        status_id = data.get("status")
        order = data.get("order")
        ticket.status = TicketStatus.objects.get(id=status_id)
        ticket.order = order
        ticket.save()
        response = ticket.__dict__
        del response["_state"]
        return JsonResponse(response)


class BulkUpdateTicketStatusAJAXView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        updated_tickets = []
        for ticket_data in data.get("tickets"):
            ticket = Ticket.objects.get(id=ticket_data.get("id"))
            status_id = ticket_data.get("status")
            order = ticket_data.get("order")
            ticket.status = TicketStatus.objects.get(id=status_id)
            ticket.order = order
            ticket.save()
            response = ticket.__dict__
            del response["_state"]
            updated_tickets.append(response)
        return JsonResponse({"updated": updated_tickets})


class BulkUpdateBoardStatusesAJAXView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        updated_statuses = []
        for status_data in data.get("statuses"):
            status = TicketStatus.objects.get(id=status_data.get("id"))
            order = status_data.get("order")
            status.order = order
            status.save()
            response = status.__dict__
            del response["_state"]
            updated_statuses.append(response)
        return JsonResponse({"updated": updated_statuses})
