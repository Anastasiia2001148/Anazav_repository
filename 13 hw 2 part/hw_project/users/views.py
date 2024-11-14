from django.views import View
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm

class RegisterView(View):
    template_name = 'users/signup.html'
    form_class = RegisterForm

    def get(self,request):
        return render(request,self.template_name, {'form': self.form_class()})

    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            messages.success(request, f'Hello {username}.Registration successfully complicated')
            return redirect(to='users:signin')
        return render(request,self.template_name,{'form': form} )

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    html_email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')
    success_message = "An email with instructions to reset your password has been sent to %(email)s."
    subject_template_name = 'users/password_reset_subject.txt'

class LoginForm(AuthenticationForm):
    pass