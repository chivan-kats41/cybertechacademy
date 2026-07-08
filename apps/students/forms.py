"""
CyberTech Academy - Student Registration Form
"""
from django import forms
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import User
from apps.students.models import StudentProfile
from apps.courses.models import Course


class StudentRegistrationForm(forms.Form):
    # Personal Info
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-input'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Phone e.g. +256 700 000 000', 'class': 'form-input'})
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Country / Location', 'class': 'form-input'})
    )

    # Course & Mode
    course_interest = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        empty_label='— Select a Course —',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    learning_mode = forms.ChoiceField(
        choices=StudentProfile.LearningMode.choices,
        widget=forms.RadioSelect(attrs={'class': 'form-radio'})
    )

    # Password
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Create Password', 'class': 'form-input'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-input'})
    )

    # Terms
    terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the Terms & Conditions to register.'}
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned

    def save(self):
        data = self.cleaned_data
        # Build username from email
        base_username = data['email'].split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=data['email'],
            password=data['password1'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            country=data['country'],
            role=User.Role.STUDENT,
        )

        StudentProfile.objects.create(
            user=user,
            course_interest=data['course_interest'],
            learning_mode=data['learning_mode'],

        )

        return user
