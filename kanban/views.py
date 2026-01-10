import json

from django.views.generic import DetailView, View
from django.http import JsonResponse
from kanban.models import Board, Ticket, TicketStatus


class BoardView(DetailView):
    template_name = "kanban/board.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = self.object.statuses.all().order_by("order")
        return context


class TicketView(DetailView):
    template_name = "kanban/ticket.html"
    model = Ticket


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
