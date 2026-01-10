"""
URL configuration for kanban project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from core import views
from kanban import views as kanban_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.HomeView.as_view(), name="index"),
    path("boards/<int:pk>/", kanban_views.BoardView.as_view(), name="board-detail"),
    path("tickets/<int:pk>/", kanban_views.TicketView.as_view(), name="ticket-detail"),
    path(
        "ajax/tickets/update-status/",
        kanban_views.UpdateTicketStatusAJAXView.as_view(),
        name="ajax-ticket-update-status",
    ),
    path(
        "ajax/tickets/bulk-update-status/",
        kanban_views.BulkUpdateTicketStatusAJAXView.as_view(),
        name="ajax-ticket-bulk-update-status",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
