from django.contrib import admin
from .models import Board, BoardMembership, Sprint, Ticket, TicketStatus

admin.site.register(Board)
admin.site.register(BoardMembership)
admin.site.register(Ticket)
admin.site.register(TicketStatus)
admin.site.register(Sprint)
