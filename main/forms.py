from django import forms


class LoginForm(forms.Form):
    login = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Логин'}), label=False)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), label=False)


class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Логин'}), label=False)
    mail = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Адрес почты'}), label=False)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), label=False)
    rep_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}), label=False)


class RedactForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput)
    title = forms.CharField(max_length=2048)
    photo = forms.CharField(max_length=4096)
    text = forms.CharField(widget=forms.Textarea)
    water_period = forms.IntegerField()
    fertilize_period = forms.IntegerField()


class ChangePassForm(forms.Form):
    cur_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Старый пароль'}), label=False)
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль'}), label=False)
    rep_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}), label=False)


class ChangeEmail(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Почта'}), label=False)


class ChangeUserName(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Логин'}), label=False)


class ForgotPassForm(forms.Form):
    mail = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Адрес почты'}), label=False)


class ConfirmMailForm(forms.Form):
    code_id = forms.IntegerField(widget=forms.HiddenInput)
    email = forms.CharField(widget=forms.HiddenInput)
    code = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': 'Код подтверждения'}), label=False)


class RestorePassForm(forms.Form):
    email = forms.CharField(widget=forms.HiddenInput)
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль'}), label=False)
    rep_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}), label=False)
