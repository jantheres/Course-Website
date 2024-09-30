from django import forms
from .models import Student
from django.core.exceptions import ValidationError
from .models import Category, Course


class StudentRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = Student
        fields = ['full_name', 'email', 'phone_number', 'date_of_birth', 'password', 'confirm_password']

    def __init__(self, *args, **kwargs):
        super(StudentRegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})  # Add class to all fields

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return confirm_password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Student.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if len(phone_number) != 10 or not phone_number.isdigit():
            raise ValidationError("Phone number must be exactly 10 digits.")
        return phone_number


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['category', 'course_name', 'description', 'duration', 'module_1', 'module_2']



class EditCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'description', 'duration', 'category']


from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['course', 'text']


# forms.py
from django import forms
from .models import Student

class EditStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'date_of_birth']


from django import forms

class RegistrationReportForm(forms.Form):
    start_date = forms.DateField(widget=forms.SelectDateWidget())
    end_date = forms.DateField(widget=forms.SelectDateWidget())



from django import forms

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email',
        'style': 'height: 50px;',  # Set input size here
    }))

# forms.py
from django import forms

class AdminPasswordResetRequestForm(forms.Form):
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
