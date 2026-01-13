from django.db.models import TextChoices


class BasicStatuses(TextChoices):
    TODO = "To do"
    IN_PROGRESS = "In progress"
    BLOCKED = "Blocked"
    DONE = "Done"
