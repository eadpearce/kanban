from django.contrib import admin
from .models import Board, BoardMembership, Ticket, TicketStatus

admin.site.register(Board)
admin.site.register(BoardMembership)
admin.site.register(Ticket)
admin.site.register(TicketStatus)
