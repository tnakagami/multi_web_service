from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, PasswordChangeForm,
    PasswordResetForm, SetPasswordForm
)
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy

User = get_user_model()

class LoginForm(AuthenticationForm):
    """
    Login form
    """
    username = forms.CharField(label=ugettext_lazy('username or e-mail address'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class UpdateUserStatusForm(forms.ModelForm):
    """
    Form of updating user status
    """
    class Meta:
        model = User
        fields = ('is_active', )

class CreateUserForm(UserCreationForm):
    """
    Form of user registeration
    """
    required_css_class = 'required'

    class Meta:
        model = User
        fields = ('username', 'email', 'viewname')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['viewname'].label = ugettext_lazy('view name')

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()

        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        User.objects.filter(username=username, is_active=False).delete()

        return username

class UpdateAccountInfoForm(forms.ModelForm):
    """
    Update Account Information
    """

    class Meta:
        model = User
        fields = ('viewname', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['viewname'].label = ugettext_lazy('view name')

class ChangePasswordForm(PasswordChangeForm):
    """
    Change own password
    """
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class RequestInitPasswordForm(PasswordResetForm):
    """
    Request initialized Password
    """
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = ugettext_lazy('There is no user registered with the specified e-mail address.')
            self.add_error('email', msg)

        return email

class ResetPasswordForm(SetPasswordForm):
    """
    Reset Password
    """
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ChangeEmailForm(forms.ModelForm):
    """
    Change E-mail address
    """
    required_css_class = 'required'

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
