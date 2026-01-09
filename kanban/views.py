import json

from django.core import serializers
from django.views.generic import DetailView, View
from django.http import JsonResponse
from kanban.models import Board, Ticket, TicketStatus


class BoardView(DetailView):
    template_name = "kanban/board.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = self.object.statuses.all()
        context["tickets"] = self.object.tickets.all()
        return context


class TicketView(DetailView):
    template_name = "kanban/ticket.html"
    model = Ticket


class UpdateTicketStatusAJAXView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        ticket = Ticket.objects.get(id=data.get("id"))
        status_id = data.get("status")
        ticket.status = TicketStatus.objects.get(id=status_id)
        ticket.save()
        response = ticket.__dict__
        del response["_state"]
        return JsonResponse(response)
