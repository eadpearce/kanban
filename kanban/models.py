from django.utils import timezone

from django.db import models
from django.contrib.auth import get_user_model

from kanban.constants import BasicStatuses, StatusColours

User = get_user_model()


class TimestampedMixin(models.Model):
    """Mixin adding timestamps for creation and last update."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Board(TimestampedMixin):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    @property
    def todo_status(self):
        return TicketStatus.objects.get(board=self, name=BasicStatuses.TODO)

    @property
    def done_status(self):
        return TicketStatus.objects.get(board=self, name=BasicStatuses.DONE)

    @property
    def active_sprint(self):
        today = timezone.now()
        return Sprint.objects.filter(
            start_date__lt=today, completed_date__isnull=True
        ).first()


class BoardMembership(models.Model):
    board = models.ForeignKey(Board, related_name="members", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="memberships", on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.board.name} membership {self.user.get_full_name()}"

    class Meta:
        unique_together = ("board", "user")


class TicketStatus(models.Model):
    name = models.CharField(max_length=100)
    board = models.ForeignKey(Board, related_name="statuses", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    colour = models.CharField(
        choices=StatusColours.choices, max_length=10, default=StatusColours.DEFAULT
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("order",)
        unique_together = ("board", "name")


class Sprint(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    board = models.ForeignKey(Board, related_name="sprints", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return (
            self.start_date
            and self.start_date < timezone.now()
            and self.completed_date is None
        )

    @property
    def is_completed(self):
        return self.start_date is not None and self.completed_date is not None


class Ticket(TimestampedMixin):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    board = models.ForeignKey(Board, related_name="tickets", on_delete=models.CASCADE)
    status = models.ForeignKey(
        TicketStatus,
        null=True,
        blank=True,
        related_name="tickets",
        on_delete=models.DO_NOTHING,
    )
    order = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(
        User,
        related_name="created_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    assignee = models.ForeignKey(
        User,
        related_name="assigned_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    sprint = models.ForeignKey(
        Sprint, related_name="tickets", on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def assignee_initials(self):
        if self.assignee.first_name and self.assignee.last_name:
            return f"{self.assignee.first_name[0].upper()} {self.assignee.last_name[0].upper()}"
        else:
            return f"{self.assignee.username[0].upper()}"

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return f"Ticket {self.id}: {self.title}"


class Comment(TimestampedMixin):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ticket = models.ForeignKey(
        Ticket, related_name="comments", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("created_at",)
