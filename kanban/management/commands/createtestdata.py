import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from kanban import factories

User = get_user_model()


class Command(BaseCommand):
    help = "Create a given number of kanban boards and all related objects"

    def add_arguments(self, parser):
        parser.add_argument("email", nargs="?", type=str)

    def handle(self, *args, **options):
        developer_user = User.objects.get(email=options["email"])

        test_users = factories.UserFactory.create_batch(10)
        users = ", ".join([f"{u.first_name} {u.last_name}" for u in test_users])
        self.stdout.write(self.style.SUCCESS(f"Created test users: {users}"))

        board = factories.BoardFactory.create()
        todo = factories.TicketStatusFactory(name="To do", board=board)
        in_progress = factories.TicketStatusFactory(name="In progress", board=board)
        done = factories.TicketStatusFactory(name="Done", board=board)
        statuses = [todo, in_progress, done]

        memberships = []

        for i, user in enumerate([developer_user] + test_users):
            if user == developer_user:
                membership = factories.BoardMembershipFactory.create(
                    board=board, user=user, is_owner=True
                )
            else:
                membership = factories.BoardMembershipFactory.create(
                    board=board, user=user
                )
            memberships.append(membership)

            tickets = factories.TicketFactory.create_batch(
                3, board=board, author=user, status=random.choice(statuses)
            )
            created_tickets = ", ".join([t.title for t in tickets])
            self.stdout.write(
                self.style.SUCCESS(f"Created tickets by user {user}: {created_tickets}")
            )

        created_memberships = ", ".join(
            [f"{m.user.first_name} {m.user.last_name}" for m in memberships]
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created memberships: {created_memberships}")
        )

        self.stdout.write(self.style.SUCCESS(f"Created test data"))
