from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Permission
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, resolve_url
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView, FormView
from .forms import (
    LoginForm, UpdateUserStatusForm, CreateUserForm, UpdateAccountInfoForm,
    ChangePasswordForm, RequestInitPasswordForm, ResetPasswordForm, ChangeEmailForm
)

User = get_user_model()

class TopPage(TemplateView):
    """
    Top Page
    """
    template_name = 'registration/top_page.html'

class LoginPage(LoginView):
    """
    Login Page
    """
    form_class = LoginForm
    template_name = 'registration/login.html'


class LogoutPage(LogoutView):
    """
    Logout Page
    """
    template_name = 'registration/top_page.html'

# =============
# For Superuser
# =============
class AccountsPage(UserPassesTestMixin, ListView):
    raise_exception = True
    model = User
    template_name = 'registration/account_list.html'
    context_object_name = 'accounts'

    def test_func(self):
        user = self.request.user
        ret = user.is_superuser

        return ret

class UpdateUserStatus(UserPassesTestMixin, UpdateView):
    raise_exception = True
    model = User
    form_class = UpdateUserStatusForm
    template_name = 'registration/account_list.html'

    def test_func(self):
        user = self.request.user
        ret = user.is_superuser

        return ret

    def form_valid(self, form):
        user = self.model.objects.get(pk=self.kwargs['pk'])
        user.is_active = not user.is_active
        user.save()

        return redirect('registration:accounts_page')

class DeleteUserPage(UserPassesTestMixin, DeleteView):
    raise_exception = True
    model = User
    template_name = 'registration/delete_user.html'
    success_url = reverse_lazy('registration:accounts_page')

    def test_func(self):
        user = self.request.user

        try:
            user_pk = self.kwargs['pk']
            target_user = self.model.objects.get(pk=user_pk)
            ret = user.is_superuser and (not target_user.is_active)
        except User.DoesNotExist:
            ret = False

        return ret

# =================
# User Registration
# =================
class CreateUser(CreateView):
    """
    Temporary User Registration
    """
    template_name = 'registration/create_user.html'
    form_class = CreateUserForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # create activation url
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'timeout': int(getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*10)) // 60,
            'user': user,
        }

        subject = render_to_string('registration/mail_template/create/subject.txt', context)
        message = render_to_string('registration/mail_template/create/message.txt', context)
        user.email_user(subject, message)

        return redirect('registration:create_user_done')

class CreateUserDone(TemplateView):
    template_name = 'registration/create_user_done.html'

class CreateUserComplete(TemplateView):
    """
    Complete User Registration
    """
    template_name = 'registration/create_user_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*10)

    def get(self, request, **kwargs):
        token = kwargs.get('token')

        try:
            user_pk = loads(token, max_age=self.timeout_seconds)
        except (SignatureExpired, BadSignature):
            response = HttpResponseBadRequest()
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                response = HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # set active
                    user.is_active = True
                    # Add permission
                    view_user = Permission.objects.get(codename='view_user')
                    view_perm = Permission.objects.get(codename='view_permission')
                    user.user_permissions.add(view_user, view_perm)
                    user.save()
                    response = super().get(request, **kwargs)
                else:
                    response = HttpResponseBadRequest()

        return response

class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        # Check primary key of user is equivalent or user is superuser
        chk_account = user.pk == self.kwargs['pk'] or user.is_superuser
        # Check permission
        chk_perm = user.has_perm('registration.view_user') and user.has_perm('auth.view_permission')
        ret = chk_account and chk_perm

        return ret

class DetailAccountInfo(OnlyYouMixin, DetailView):
    """
    Detail Account Information
    """
    model = User
    template_name = 'registration/detail_account_info.html'

class UpdateAccountInfo(OnlyYouMixin, UpdateView):
    """
    Update Account Information
    """
    model = User
    form_class = UpdateAccountInfoForm
    template_name = 'registration/update_account_info_form.html'

    def get_success_url(self):
        return resolve_url('registration:detail_account_info', pk=self.kwargs['pk'])

class DeleteOwnAccount(OnlyYouMixin, DeleteView):
    """
    Delete Own Account
    """
    raise_exception = True
    model = User
    success_url = reverse_lazy('registration:login')

    def get(self, request, *args, **kwargs):
        # ignore direct access
        return self.handle_no_permission()

# ===============
# Change Password
# ===============
class ChangePssword(PasswordChangeView):
    """
    Change Own Password
    """
    form_class = ChangePasswordForm
    success_url = reverse_lazy('registration:password_change_complete')
    template_name = 'registration/change_password.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()

        return super().form_valid(form)

class ChangePassowrdComplete(PasswordChangeDoneView):
    """
    Complete Change Own Password
    """
    template_name = 'registration/change_password_complete.html'

# ==============
# Reset Password
# ==============
class ResetPassword(PasswordResetView):
    subject_template_name = 'registration/mail_template/reset_password/subject.txt'
    email_template_name = 'registration/mail_template/reset_password/message.txt'
    template_name = 'registration/reset_password_form.html'
    form_class = RequestInitPasswordForm
    success_url = reverse_lazy('registration:reset_password_done')

class ResetPasswordDone(PasswordResetDoneView):
    template_name = 'registration/reset_password_done.html'

class ResetPasswordConfirm(PasswordResetConfirmView):
    form_class = ResetPasswordForm
    success_url = reverse_lazy('registration:reset_password_complete')
    template_name = 'registration/reset_password_confirm.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()

        return super().form_valid(form)

class ResetPasswordComplete(PasswordResetCompleteView):
    template_name = 'registration/reset_password_complete.html'

# =====================
# Change E-mail address
# =====================
class ChangeEmail(LoginRequiredMixin, FormView):
    """
    Change Email address
    """
    template_name = 'registration/change_email_form.html'
    form_class = ChangeEmailForm

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data['email']

        # Send to URL
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'param': dumps(user.pk),
            'token': dumps(new_email),
            'timeout': int(getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*10)) // 60,
            'user': user,
        }

        subject = render_to_string('registration/mail_template/change_email/subject.txt', context)
        message = render_to_string('registration/mail_template/change_email/message.txt', context)
        send_mail(subject, message, None, [new_email])

        return redirect('registration:change_email_done')

class ChangeEmailDone(LoginRequiredMixin, TemplateView):
    template_name = 'registration/change_email_done.html'

class ChangeEmailComplete(LoginRequiredMixin, TemplateView):
    template_name = 'registration/change_email_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*10)

    def get(self, request, **kwargs):
        param = kwargs.get('param')
        token = kwargs.get('token')

        try:
            user_pk = loads(param, max_age=self.timeout_seconds)
            new_email = loads(token, max_age=self.timeout_seconds)
        except (SignatureExpired, BadSignature):
            response = HttpResponseBadRequest()
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                response = HttpResponseBadRequest()
            else:
                # Check primary key of user
                if user_pk == request.user.pk and user.is_active:
                    user.email = new_email
                    user.save()
                    response = super().get(request, **kwargs)
                else:
                    response = HttpResponseBadRequest()

        return response
