from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', max_length=150, required=True)
    last_name = forms.CharField(label='Фамилия', max_length=150, required=False)
    email = forms.EmailField(label='Email', required=True)
    birthday = forms.DateField(
        label='Дата рождения',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.email = self.cleaned_data.get('email', '')
            user.save(update_fields=['first_name', 'last_name', 'email'])
            user.profile.birthday = self.cleaned_data.get('birthday')
            user.profile.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = False


class ProfileDetailForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['birthday', 'avatar']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birthday'].required = True
        self.fields['birthday'].empty_label = None
        if self.instance and self.instance.pk and self.instance.birthday:
            self.fields['birthday'].initial = self.instance.birthday.strftime('%Y-%m-%d')
