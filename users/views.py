from django.views.generic import TemplateView


class RegisterView(TemplateView):
    template_name = 'register.html'


class LoginView(TemplateView):
    template_name = 'login.html'


class ProfileView(TemplateView):
    template_name = 'profile.html'