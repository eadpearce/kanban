from django.db import models


class Board(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"Board {self.id}: {self.name}"


class TicketStatus(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"Status {self.id}: {self.name}"


class Ticket(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    board = models.OneToOneField(
        Board, related_name="tickets", on_delete=models.CASCADE
    )
    status = models.ForeignKey(
        TicketStatus,
        null=True,
        blank=True,
        related_name="tickets",
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return f"Ticket {self.id}: {self.title}"
