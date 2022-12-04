from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Getting page with information about website creator."""

    template_name: str = 'about/author.html'


class AboutTechView(TemplateView):
    """Getting page with information about used technilogy in project."""

    template_name: str = 'about/tech.html'
