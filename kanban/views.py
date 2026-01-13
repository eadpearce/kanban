import json

from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import DetailView, View, FormView, ListView, UpdateView
from django.http import JsonResponse
from kanban.models import Board, Ticket, TicketStatus
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

        return self.get_success_url(board.id)


class EditBoardView(UpdateView):
    form_class = forms.BoardEditForm
    template_name = "core/form.html"
    queryset = Board.objects.all()

    def get_success_url(self, board_id):
        return redirect(reverse("board-detail", kwargs={"pk": board_id}))

    def form_valid(self, form):
        data = form.cleaned_data
        self.object.name = (data["name"],)
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
        return context


class BoardSettingsView(DetailView):
    template_name = "kanban/board_settings.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = self.object.statuses.all().order_by("order")
        return context


class BoardEditColumnsView(DetailView):
    template_name = "kanban/board_edit_columns.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = self.object.statuses.all().order_by("order")
        return context


class BacklogView(ListView):
    template_name = "kanban/backlog.html"
    model = Ticket

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(board__id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["board"] = Board.objects.get(pk=self.kwargs["pk"])
        return context


class TicketView(DetailView):
    template_name = "kanban/ticket.html"
    model = Ticket


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
