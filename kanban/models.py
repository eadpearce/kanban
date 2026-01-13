from django.db import models
from django.contrib.auth import get_user_model

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
        return f"Board {self.id}: {self.name}"


class TicketStatus(models.Model):
    name = models.CharField(max_length=100)
    board = models.ForeignKey(Board, related_name="statuses", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Status {self.id}: {self.name}"

    class Meta:
        ordering = ("order",)


class Ticket(TimestampedMixin):
    title = models.CharField(max_length=200)
    description = models.TextField()
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

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return f"Ticket {self.id}: {self.title}"
