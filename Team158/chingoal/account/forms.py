from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class MyAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Password'}))

class RegistrationForm(UserCreationForm):
    username = forms.CharField(max_length = 30, widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Username','autofocus':'true'}))
    password1 = forms.CharField(max_length = 200, label = 'Password',
                                widget = forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    password2 = forms.CharField(max_length = 200, label = 'Confirm Password',
        widget = forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm password'}))
    email = forms.EmailField(widget = forms.EmailInput(attrs={'class':'form-control','placeholder':'E-mail'}))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2','email')

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact = username):
            raise forms.ValidationError('Username is already taken!')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact = email):
            raise forms.ValidationError('Email address is registered!')
        return email
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.is_active = False # not active until he opens activation link
            user.save()
        return user



class EditProfileForm(forms.Form):
    photo = forms.ImageField(label = 'Upload a photo', required = False)
    bio = forms.CharField(max_length = 420, label = 'Short bio ', required = False, widget=forms.Textarea(attrs={'placeholder': 'optional','class':'form-control'}))
    password1 = forms.CharField(max_length = 40, label = 'Old password ', widget = forms.PasswordInput(attrs={'required': True, 'placeholder': 'required','class':'form-control input-md'}))
    password2 = forms.CharField(max_length = 40, label = 'New password ', required = False, widget = forms.PasswordInput(attrs={'placeholder': 'optional','class':'form-control input-md'}))
    password3 = forms.CharField(max_length = 40, label = 'Confirm password ', required = False, widget = forms.PasswordInput(attrs={'placeholder': 'optional','class':'form-control input-md'}))
    
    def clean(self):
        cleaned_data = super(EditProfileForm, self).clean()
        password3 = cleaned_data.get('password3')
        password2 = cleaned_data.get('password2')
        if password2 != password3:
            raise forms.ValidationError('New passwords didn\'t match.')
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact = username):
            raise forms.ValidationError('Username is already taken!')
        return username


class EditScheduleForm(forms.Form):
    LEVELS = (
        ('0','Zero level'),
        ('1','One level'),
        ('2','Two levels'),
        ('3','Three levels'),
        ('4','Four levels'),
        ('5','Five levels'),
    )
    LESSONS = (
        ('1','One lesson'),
        ('2','Two lessons'),
        ('3','Three lessons'),
        ('4','Four lessons'),
        ('5','Five lessons'),
    )
    progress_level = forms.ChoiceField(choices=LEVELS, label="Levels per day", widget=forms.Select())
    progress_lesson = forms.ChoiceField(choices=LESSONS, label="Lessons per day", widget=forms.Select())

    def clean(self):
        cleaned_data = super(EditScheduleForm, self).clean()
        return cleaned_data

    ## TODO clean_process_level clean_process_lesson


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(max_length = 200, label = 'Password',
        widget = forms.PasswordInput())
    password2 = forms.CharField(max_length = 200, label = 'Confirm Password',
        widget = forms.PasswordInput())

    def clean(self):
        # Get dictionary of cleaned data
        cleaned_data = super(ResetPasswordForm, self).clean()
        # Check two passwords match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")
        # return cleaned data
        return cleaned_data



