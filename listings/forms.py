from django import forms
from .models import CustomUser, Profile, Contact
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# CustomUserCreationForm is used to create a new user
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role', 'phone_number', 'address', 'profile_picture', 'date_of_birth')
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }
        labels = {
            'username': 'Username',
            'email': 'Email',
            'password1': 'Password',
            'password2': 'Confirm Password',
            'role': 'Role',
            'phone_number': 'Phone Number',
            'address': 'Address',
            'profile_picture': 'Profile Picture',
            'date_of_birth': 'Date of Birth',
        }
        help_texts = {
            'username': 'Enter a unique username.',
            'email': 'Enter a valid email address.',
            'password1': 'Enter a strong password.',
            'password2': 'Re-enter the password for confirmation.',
            'role': 'Select your role.',
            'phone_number': 'Enter your phone number.',
            'address': 'Enter your address.',
            'profile_picture': 'Upload a profile picture.',
            'date_of_birth': 'Enter your date of birth.',
        }
        error_messages = {
            'username': {
                'required': 'Username is required.',
                'unique': 'This username is already taken.',
            },
            'email': {
                'required': 'Email is required.',
                'invalid': 'Enter a valid email address.',
            },
            'password1': {
                'required': 'Password is required.',
                'too_short': 'Password must be at least 8 characters long.',
            },
            'password2': {
                'required': 'Confirm Password is required.',
                'mismatch': 'Passwords do not match.',
            },
        }

# CustomUserChangeForm is used to update the user's information
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'phone_number', 'address', 'profile_picture', 'date_of_birth')
        widgets = {
            'password': forms.PasswordInput(),
        }
        labels = {
            'username': 'Username',
            'email': 'Email',
            'role': 'Role',
            'phone_number': 'Phone Number',
            'address': 'Address',
            'profile_picture': 'Profile Picture',
            'date_of_birth': 'Date of Birth',
        }
        help_texts = {
            'username': 'Enter a unique username.',
            'email': 'Enter a valid email address.',
            'role': 'Select your role.',
            'phone_number': 'Enter your phone number.',
            'address': 'Enter your address.',
            'profile_picture': 'Upload a profile picture.',
            'date_of_birth': 'Enter your date of birth.',
        }
        error_messages = {
            'username': {
                'required': 'Username is required.',
                'unique': 'This username is already taken.',
            },
            'email': {
                'required': 'Email is required.',
                'invalid': 'Enter a valid email address.',
            },
            'role': {
                'required': 'Role is required.',
            },
            'phone_number': {
                'invalid': 'Enter a valid phone number.',
            },
        }


# ProfileForm is used to update the user's profile information
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'profile_picture', 'phone_number', 'address', 'date_of_birth')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'profile_picture': forms.ClearableFileInput(),
            'phone_number': forms.TextInput(),
            'address': forms.TextInput(),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'bio': 'Bio',
            'profile_picture': 'Profile Picture',
            'phone_number': 'Phone Number',
            'address': 'Address',
            'date_of_birth': 'Date of Birth',
        }
        help_texts = {
            'bio': 'Write a short bio about yourself.',
            'profile_picture': 'Upload a new profile picture.',
            'phone_number': 'Enter your phone number.',
            'address': 'Enter your address.',
            'date_of_birth': 'Enter your date of birth.',
        }
        error_messages = {
            'bio': {
                'required': 'Bio is required.',
            },
            'profile_picture': {
                'invalid': 'Upload a valid image file.',
            },
            'phone_number': {
                'invalid': 'Enter a valid phone number.',
            },
            'address': {
                'required': 'Address is required.',
            },
            'date_of_birth': {
                'invalid': 'Enter a valid date of birth.',
            },
        }

class ContactForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Contact
        fields = ('name', 'email', 'message')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if not name.strip():
            raise forms.ValidationError('Name cannot be empty.')
        return name

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.strip():
            raise forms.ValidationError('Email cannot be empty.')
        return email

    def clean_message(self):
        message = self.cleaned_data['message']
        if not message.strip():
            raise forms.ValidationError('Message cannot be empty.')
        return message

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        message = cleaned_data.get('message')

        if not name.strip():
            self.add_error('name', 'Name cannot be empty.')
        if not email.strip():
            self.add_error('email', 'Email cannot be empty.')
        if not message.strip():
            self.add_error('message', 'Message cannot be empty.')

        return cleaned_data