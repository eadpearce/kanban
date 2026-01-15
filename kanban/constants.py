from django.db.models import TextChoices


class BasicStatuses(TextChoices):
    TODO = "To do"
    IN_PROGRESS = "In progress"
    BLOCKED = "Blocked"
    DONE = "Done"


class StatusColours(TextChoices):
    """
    Each colour corresponds to a govuk-tag--{colour} class.
    https://design-system.service.gov.uk/components/tag/
    """

    DEFAULT = "grey"
    GREEN = "green"
    TURQUOISE = "turquoise"
    BLUE = "blue"
    LIGHT_BLUE = "light-blue"
    PURPLE = "purple"
    PINK = "pink"
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"


DEFAULT_COLOUR_MAPPING = {
    BasicStatuses.TODO: StatusColours.DEFAULT,
    BasicStatuses.IN_PROGRESS: StatusColours.DEFAULT,
    BasicStatuses.BLOCKED: StatusColours.RED,
    BasicStatuses.DONE: StatusColours.GREEN,
}
