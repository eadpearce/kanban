import json

from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import DetailView, View, FormView, ListView, UpdateView
from django.http import JsonResponse
from kanban.models import Board, Ticket, TicketStatus
from kanban import forms


class BoardView(DetailView):
    template_name = "kanban/board.html"
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

    def get_success_url(self, board_id):
        return redirect(reverse("ticket-detail", kwargs={"pk": self.object.id}))

    def form_valid(self, form):
        data = form.cleaned_data
        self.object.title = data["title"]
        self.object.description = data["description"]
        self.object.save()
        return self.get_success_url(self.object.board.id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["ticket_id"] = self.object.id
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
