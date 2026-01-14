import json
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import (
    DetailView,
    View,
    FormView,
    ListView,
    UpdateView,
    TemplateView,
)
from django.http import JsonResponse
from kanban.models import Board, BoardMembership, Ticket, TicketStatus, Sprint, User
from kanban import forms
from kanban.constants import BasicStatuses


class CreateBoardView(FormView):
    form_class = forms.BoardCreateForm
    template_name = "core/form.html"

    def get_success_url(self, board_id):
        return redirect(reverse("board-detail", kwargs={"pk": board_id}))

    def form_valid(self, form):
        data = form.cleaned_data
        board = Board.objects.create(
            name=data["name"],
        )
        # create basic statuses by default
        for i, name in enumerate(BasicStatuses.values):
            TicketStatus.objects.create(name=name, board=board, order=i)

        BoardMembership.objects.create(
            board=board, user=self.request.user, is_owner=True
        )

        return self.get_success_url(board.id)


class EditBoardView(UpdateView):
    form_class = forms.BoardEditForm
    template_name = "core/form.html"
    queryset = Board.objects.all()

    def get_success_url(self, board_id):
        return redirect(reverse("board-detail", kwargs={"pk": board_id}))

    def form_valid(self, form):
        data = form.cleaned_data
        self.object.name = data["name"]
        self.object.save()
        return self.get_success_url(self.object.id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board_id"] = self.kwargs.get("pk")
        return kwargs


class BoardView(DetailView):
    template_name = "kanban/board.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = self.object.statuses.all().order_by("order")
        user_member = BoardMembership.objects.filter(
            board=self.object, user=self.request.user
        )
        context["is_member"] = user_member.exists()
        if user_member.exists():
            context["is_owner"] = user_member.first().is_owner
        else:
            context["is_owner"] = False
        return context


class BoardSettingsView(DetailView):
    template_name = "kanban/board_settings.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = self.object.statuses.all().order_by("order")
        context["owner"] = self.object.members.filter(is_owner=True).first().user
        user_member = BoardMembership.objects.filter(
            board=self.object, user=self.request.user
        )
        context["is_member"] = user_member.exists()
        if user_member.exists():
            context["is_owner"] = user_member.first().is_owner
        else:
            context["is_owner"] = False
        return context


class BoardEditColumnsView(DetailView):
    template_name = "kanban/board_edit_columns.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = self.object.statuses.all().order_by("order")
        return context

    def post(self, request, *args, **kwargs):
        selected_statuses = request.POST.getlist("selected_status")
        action = request.POST.get("form-action")
        if action == "delete":
            statuses = TicketStatus.objects.filter(id__in=selected_statuses)
            column_names = ", ".join([f"“{status.name}”" for status in statuses])
            tickets = Ticket.objects.filter(status__id__in=statuses)
            tickets.update(status=None)
            for ticket in tickets:
                ticket.save()
            statuses.delete()
            messages.success(
                request,
                f"Column(s) {column_names} deleted. Any associated tickets have been moved to the backlog",
            )
        board = Board.objects.get(pk=self.kwargs["pk"])
        return redirect(reverse("board-edit-columns", kwargs={"pk": board.pk}))


class ManageMembershipsView(ListView):
    template_name = "kanban/manage_memberships.html"
    model = BoardMembership

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(board__id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = Board.objects.get(pk=self.kwargs["pk"])
        context["board"] = board
        context["statuses"] = board.statuses.all().order_by("order")
        user_member = BoardMembership.objects.filter(
            board=board, user=self.request.user
        )
        context["is_member"] = user_member.exists()
        if user_member.exists():
            context["is_owner"] = user_member.first().is_owner
        else:
            context["is_owner"] = False
        return context

    def post(self, request, *args, **kwargs):
        selected_members = request.POST.getlist("selected_members")
        action = request.POST.get("form-action")
        members = BoardMembership.objects.filter(id__in=selected_members)
        member_names = ", ".join([m.user.get_full_name() for m in members])

        if action == "remove":
            members.delete()
            if len(selected_members) > 1:
                success_message = (
                    f"Members {member_names} have been removed from this board"
                )
            else:
                success_message = (
                    f"Member {member_names} has been removed from this board"
                )
            messages.success(
                request,
                success_message,
            )
        elif action == "make-owner":
            for member in members:
                member.is_owner = True
                member.save()
            if len(members) > 1:
                success_message = (
                    f"Members {member_names} have been made owners of this board"
                )
            else:
                success_message = (
                    f"Member {member_names} has been made an owner of this board"
                )
            messages.success(
                request,
                success_message,
            )
        return redirect(
            reverse("board-manage-memberships", kwargs={"pk": self.kwargs["pk"]})
        )


class CreateMembershipView(FormView):
    form_class = forms.CreateMembershipForm
    template_name = "core/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board_id"] = self.kwargs["pk"]
        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        board = Board.objects.get(pk=self.kwargs["pk"])
        user = data["user"]
        BoardMembership.objects.create(board=board, user=user, is_owner=False)
        return redirect(
            reverse("board-manage-memberships", kwargs={"pk": self.kwargs["pk"]})
        )


class BacklogView(ListView):
    template_name = "kanban/backlog.html"
    model = Ticket

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            board__id=self.kwargs["pk"], status__isnull=True, sprint__isnull=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = Board.objects.get(pk=self.kwargs["pk"])
        context["board"] = board
        context["statuses"] = board.statuses.all().order_by("order")
        user_member = BoardMembership.objects.filter(
            board=board, user=self.request.user
        )
        context["is_member"] = user_member.exists()
        if user_member.exists():
            context["is_owner"] = user_member.first().is_owner
        else:
            context["is_owner"] = False
        board_sprints = Sprint.objects.filter(board=board, completed_date__isnull=True)
        sprints = [
            {
                "name": "Backlog",
                "is_active": False,
                "id": "backlog",
                "tickets": self.object_list,
            }
        ]
        tickets_by_sprint = [
            {
                "name": sprint.name,
                "is_active": sprint.is_active,
                "id": sprint.id,
                "tickets": sprint.tickets.all(),
            }
            for sprint in board_sprints
        ]
        tickets_by_sprint += sprints
        active_sprint_tickets = list(
            filter(lambda x: x["is_active"], tickets_by_sprint)
        )
        inactive_sprint_tickets = list(
            filter(lambda x: not x["is_active"], tickets_by_sprint)
        )
        context["sprints"] = active_sprint_tickets + inactive_sprint_tickets
        return context

    def post(self, request, *args, **kwargs):
        selected_tickets = request.POST.getlist("selected_tickets")
        action = request.POST.get("form-action")
        tickets = Ticket.objects.filter(id__in=selected_tickets)
        ticket_titles = ", ".join([f"“{ticket.title}”" for ticket in tickets])

        if action == "delete":
            tickets.delete()
            messages.success(
                request,
                f"Ticket(s) {ticket_titles} deleted",
            )
        elif action == "update-status":
            status_id = request.POST.get("status")
            status = TicketStatus.objects.get(id=status_id)
            for ticket in tickets:
                ticket.status = status
                ticket.save()
            messages.success(
                request,
                f"Ticket(s) {ticket_titles} moved to “{status.name}”",
            )
        return self.get(request)


class SprintStartView(FormView):
    template_name = "core/form.html"
    form_class = forms.SprintStartForm

    @property
    def sprint(self):
        return Sprint.objects.get(pk=self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board"] = self.sprint.board
        return kwargs

    def form_valid(self, form):
        active_sprint = self.sprint.board.active_sprint
        if active_sprint:
            active_sprint.start_date = None
            active_sprint.save()

        tickets = Ticket.objects.filter(board=self.sprint.board, status__isnull=False)
        for ticket in tickets:
            ticket.status = None
            ticket.save()

        sprint = self.sprint
        sprint.start_date = timezone.now()
        sprint.save()

        first_status = (
            TicketStatus.objects.filter(board=sprint.board).order_by("order").first()
        )
        for ticket in sprint.tickets.all():
            ticket.status = first_status
            ticket.save()
        return redirect(reverse("board-detail", kwargs={"pk": sprint.board.pk}))


class SprintCompleteView(FormView):
    template_name = "core/form.html"
    form_class = forms.SprintCompleteForm

    @property
    def sprint(self):
        return Sprint.objects.get(pk=self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board"] = self.sprint.board
        return kwargs

    def form_valid(self, form):
        sprint = self.sprint
        done = TicketStatus.objects.get(board=sprint.board, name="Done")
        all_tickets = Ticket.objects.filter(board=sprint.board, sprint=sprint)
        unfinished_tickets = all_tickets.exclude(status=done)

        for ticket in unfinished_tickets:
            ticket.status = None
            ticket.sprint = None
            ticket.save()

        sprint.completed_date = timezone.now()
        sprint.save()

        return redirect(reverse("board-detail", kwargs={"pk": sprint.board.pk}))


class TicketView(TemplateView):
    template_name = "kanban/ticket.html"

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        data = request.POST
        obj = Ticket.objects.get(pk=self.kwargs["pk"])

        if data["field_name"] == "assignee":
            form = forms.TicketAssigneeForm(
                data=data, instance=obj, board_id=obj.board.id
            )
            if not form.is_valid():
                return self.form_invalid(form)
            obj.assignee = User.objects.get(id=data["assignee"])

        if data["field_name"] == "status":
            form = forms.TicketStatusForm(
                data=data,
                instance=obj,
                board_id=obj.board.id,
                status_initial=obj.status,
            )
            if not form.is_valid():
                return self.form_invalid(form)
            if data["status"]:
                obj.status = TicketStatus.objects.get(id=data["status"])
            else:
                obj.status = None

        if data["field_name"] == "title":
            form = forms.TicketTitleForm(instance=obj, data=data)
            if not form.is_valid():
                return self.form_invalid(form)
            obj.title = data["title"]

        if data["field_name"] == "description":
            form = forms.TicketDescriptionForm(instance=obj, data=data)
            if not form.is_valid():
                return self.form_invalid(form)
            obj.description = data["description"]

        obj.save()
        print(obj.__dict__)
        return redirect(reverse("ticket-detail", kwargs={"pk": obj.pk}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = Ticket.objects.get(pk=self.kwargs["pk"])
        context["object"] = obj
        context["users"] = User.objects.all()
        context["title_form"] = forms.TicketTitleForm(instance=obj)
        context["assignee_form"] = forms.TicketAssigneeForm(
            instance=obj, board_id=obj.board.id
        )
        context["status_form"] = forms.TicketStatusForm(
            instance=obj,
            board_id=obj.board.id,
            status_initial=obj.status,
        )
        context["description_form"] = forms.TicketDescriptionForm(instance=obj)
        context["fields"] = json.dumps(["title", "assignee", "status", "description"])
        is_member = BoardMembership.objects.filter(
            board=obj.board, user=self.request.user
        ).exists()
        context["is_member"] = is_member
        return context


class CreateTicketView(FormView):
    form_class = forms.TicketCreateForm
    template_name = "core/form.html"

    def get_success_url(self, board_id):
        return redirect(reverse("board-detail", kwargs={"pk": board_id}))

    def form_valid(self, form):
        data = form.cleaned_data
        author = User.objects.get(id=self.request.user.id)
        board = Board.objects.get(pk=self.kwargs.get("pk"))
        Ticket.objects.create(
            title=data["title"],
            description=data["description"],
            status=data["status"],
            board=board,
            author=author,
        )
        return self.get_success_url(board.id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board_id"] = self.kwargs.get("pk")
        return kwargs


class CreateStatusView(FormView):
    form_class = forms.StatusCreateForm
    template_name = "core/form.html"

    def get_success_url(self, board_id):
        return redirect(reverse("board-edit-columns", kwargs={"pk": board_id}))

    def form_valid(self, form):
        data = form.cleaned_data
        board = Board.objects.get(pk=self.kwargs.get("pk"))
        TicketStatus.objects.create(
            name=data["name"],
            board=board,
        )
        return self.get_success_url(board.id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["board_id"] = self.kwargs.get("pk")
        return kwargs


class CreateSprintView(FormView):
    form_class = forms.SprintCreateForm
    template_name = "core/form.html"

    def form_valid(self, form):
        data = form.cleaned_data
        board = Board.objects.get(pk=self.kwargs.get("pk"))
        Sprint.objects.create(
            name=data["name"],
            board=board,
        )
        return redirect(reverse("board-backlog", kwargs={"pk": self.kwargs["pk"]}))


class EditTicketView(UpdateView):
    form_class = forms.TicketEditForm
    template_name = "core/form.html"
    queryset = Ticket.objects.all()

    def get_success_url(self):
        return redirect(reverse("ticket-detail", kwargs={"pk": self.object.id}))

    def form_valid(self, form):
        data = form.cleaned_data
        self.object.title = data["title"]
        self.object.description = data["description"]
        self.object.status = data["status"]
        self.object.save()
        return self.get_success_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["ticket_id"] = self.object.id
        kwargs["board_id"] = self.object.board.id
        kwargs["status_initial"] = self.object.status
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


class BulkUpdateTicketSprintAJAXView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        updated_tickets = []
        for ticket_data in data.get("tickets"):
            ticket = Ticket.objects.get(id=ticket_data.get("id"))
            sprint_id = ticket_data.get("sprint")
            order = ticket_data.get("order")
            ticket.sprint = Sprint.objects.get(id=sprint_id)
            ticket.order = order
            ticket.save()
            response = ticket.__dict__
            del response["_state"]
            updated_tickets.append(response)
        return JsonResponse({"updated": updated_tickets})


class BulkUpdateBoardStatusesAJAXView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        updated_statuses = []
        for status_data in data.get("statuses"):
            status = TicketStatus.objects.get(id=status_data.get("id"))
            order = status_data.get("order")
            status.order = order
            status.save()
            response = status.__dict__
            del response["_state"]
            updated_statuses.append(response)
        return JsonResponse({"updated": updated_statuses})
