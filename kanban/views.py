from django.views.generic import DetailView
from kanban.models import Board, Ticket


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
