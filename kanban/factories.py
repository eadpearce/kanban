import string
import factory.fuzzy
from django.contrib.auth import get_user_model
from kanban import models


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.fuzzy.FuzzyText(length=12, chars=string.ascii_letters)
    email = factory.LazyAttribute(lambda o: f"test.user+{o.username}@example.com")
    password = "12345"
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = get_user_model()


class BoardFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=20)

    class Meta:
        model = models.Board


class BoardMembershipFactory(factory.django.DjangoModelFactory):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.BoardMembership


class TicketStatusFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=20)
    board = factory.SubFactory(BoardFactory)
    order = 0

    class Meta:
        model = models.TicketStatus


class TicketFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text", max_nb_chars=20)
    description = factory.Faker("paragraph")
    board = factory.SubFactory(BoardFactory)
    status = factory.SubFactory(TicketStatusFactory)
    order = 0
    author = factory.SubFactory(UserFactory)
    assignee = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Ticket
