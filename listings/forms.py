from django import forms
from .models import CustomUser, Profile, Contact
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import LandProperties, HousingProperties, CarProperties

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='Username',
        help_text='Enter a unique username.',
        error_messages={
            'required': 'Username is required.',
            'unique': 'This username is already taken.',
        }
    )
    email = forms.EmailField(
        label='Email',
        help_text='Enter a valid email address.',
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.',
        }
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        help_text='Enter a strong password.',
        error_messages={
            'required': 'Password is required.',
            'too_short': 'Password must be at least 8 characters long.',
        }
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(),
        help_text='Re-enter the password for confirmation.',
        error_messages={
            'required': 'Confirm Password is required.',
            'mismatch': 'Passwords do not match.',
        }
    )
    phone_number = forms.CharField(
        label='Phone Number',
        help_text='Enter your phone number.',
        required=False
    )
    address = forms.CharField(
        label='Address',
        help_text='Enter your address.',
        required=False
    )
    profile_picture = forms.ImageField(
        label='Profile Picture',
        help_text='Upload a profile picture.',
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2',
                  'phone_number', 'address', 'profile_picture')


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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'profile_picture', 'phone_number', 'address', 'date_of_birth')
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full border border-gray-400 rounded-lg px-4 py-3'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'w-full border border-gray-400 rounded-lg px-4 py-3'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full border border-gray-400 rounded-lg px-4 py-3'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full border border-gray-400 rounded-lg px-4 py-3'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full border border-gray-400 rounded-lg px-4 py-3'
            }),
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
        
# This allows, agents and sellers to create listings.
class LandPropertyForm(forms.ModelForm):
    class Meta:
        model = LandProperties
        exclude = ['owner', 'slug', 'created_at', 'updated_at']

class HousingPropertyForm(forms.ModelForm):
    class Meta:
        model = HousingProperties
        exclude = ['owner', 'slug', 'created_at', 'updated_at']

class CarPropertyForm(forms.ModelForm):
    class Meta:
        model = CarProperties
        exclude = ['owner', 'slug', 'created_at', 'updated_at']