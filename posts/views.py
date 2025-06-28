from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'


class CreateView(TemplateView):
    template_name = 'create.html'


class DirectView(TemplateView):
    template_name = 'direct.html'


class ExploreView(TemplateView):
    template_name = 'explore.html'

class MessagesView(TemplateView):
    template_name = 'messages.html'


class NotificationsView(TemplateView):
    template_name = 'notifications.html'


class ReelsView(TemplateView):
    template_name = 'reels.html'


class SearchView(TemplateView):
    template_name = 'search.html'
