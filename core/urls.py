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
    path("boards/create/", kanban_views.CreateBoardView.as_view(), name="board-create"),
    path(
        "boards/<int:pk>/tickets/create/",
        kanban_views.CreateTicketView.as_view(),
        name="create-ticket",
    ),
    path("boards/<int:pk>/", kanban_views.BoardView.as_view(), name="board-detail"),
    path(
        "sprints/<int:pk>/start/",
        kanban_views.SprintStartView.as_view(),
        name="sprint-start",
    ),
    path(
        "sprints/<int:pk>/complete/",
        kanban_views.SprintCompleteView.as_view(),
        name="sprint-complete",
    ),
    path(
        "boards/<int:pk>/sprint/create/",
        kanban_views.CreateSprintView.as_view(),
        name="sprint-create",
    ),
    path(
        "boards/<int:pk>/status/create/",
        kanban_views.CreateStatusView.as_view(),
        name="status-create",
    ),
    path(
        "boards/<int:pk>/settings/",
        kanban_views.BoardSettingsView.as_view(),
        name="board-settings",
    ),
    path(
        "boards/<int:pk>/edit-columns/",
        kanban_views.BoardEditColumnsView.as_view(),
        name="board-edit-columns",
    ),
    path(
        "boards/<int:pk>/manage-memberships/",
        kanban_views.ManageMembershipsView.as_view(),
        name="board-manage-memberships",
    ),
    path(
        "boards/<int:pk>/create-membership/",
        kanban_views.CreateMembershipView.as_view(),
        name="board-create-membership",
    ),
    path(
        "boards/<int:pk>/edit/", kanban_views.EditBoardView.as_view(), name="board-edit"
    ),
    path(
        "boards/<int:pk>/backlog/",
        kanban_views.BacklogView.as_view(),
        name="board-backlog",
    ),
    path("tickets/<int:pk>/", kanban_views.TicketView.as_view(), name="ticket-detail"),
    path(
        "tickets/<int:pk>/edit/",
        kanban_views.EditTicketView.as_view(),
        name="ticket-edit",
    ),
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
    path(
        "ajax/tickets/bulk-update-sprint/",
        kanban_views.BulkUpdateTicketSprintAJAXView.as_view(),
        name="ajax-ticket-bulk-update-sprint",
    ),
    path(
        "ajax/statuses/bulk-update/",
        kanban_views.BulkUpdateBoardStatusesAJAXView.as_view(),
        name="ajax-statuses-bulk-update",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
