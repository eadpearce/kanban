from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>/", views.BoardView.as_view(), name="board-detail"),
    path("tickets/<int:pk>/", views.TicketView.as_view(), name="ticket-detail"),
]
