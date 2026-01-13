from django.views.generic import TemplateView

from kanban.models import Board


class HomeView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_boards"] = Board.objects.all()
        context["your_boards"] = Board.objects.filter(members__user=self.request.user)
        return context
