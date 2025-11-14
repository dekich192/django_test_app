from django.shortcuts import render
from django.views.generic import TemplateView


class MenuView(TemplateView):
    """View for displaying the menu."""
    template_name = 'menu/menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context
