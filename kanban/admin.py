from django.contrib import admin
from .models import Board, Ticket, TicketStatus

admin.site.register(Board)
admin.site.register(Ticket)
admin.site.register(TicketStatus)
