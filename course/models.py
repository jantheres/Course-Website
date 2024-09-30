from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    password = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


from django.db import models
from django.contrib.auth.models import User

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    name = models.CharField(max_length=100)  
    email = models.EmailField(max_length=255, unique=True)  
    phone = models.CharField(max_length=15) 
    username = models.CharField(max_length=30, unique=True) 
    password = models.CharField(max_length=128)  

    @property
    def userid(self):
        return self.user.id  

    def __str__(self):
        return self.username
    
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.TimeField()

    module_1 = models.URLField(blank=False)  # Required field
    module_2 = models.URLField(blank=True, null=True)  # Optional field
    module_3 = models.URLField(blank=True, null=True)  # Optional field
    module_4 = models.URLField(blank=True, null=True)  # Optional field
    module_5 = models.URLField(blank=True, null=True)  # Optional field
    module_6 = models.URLField(blank=True, null=True)  # Optional field
    module_7 = models.URLField(blank=True, null=True)  # Optional field
    module_8 = models.URLField(blank=True, null=True)  # Optional field
    module_9 = models.URLField(blank=True, null=True)  # Optional field
    module_10 = models.URLField(blank=True, null=True)  # Optional field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course_name


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # Prevents multiple enrollments for the same course

    def __str__(self):
        return f'{self.student.full_name} enrolled in {self.course.course_name}'
    


from django.db import models
from django.contrib.auth.models import User

class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.IntegerField()  # Assuming you are using course IDs as integers
    completed_videos = models.IntegerField(default=0)
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - Course {self.course_id}'




class UserProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    current_video_index = models.IntegerField(default=0)  # Tracks the current video being watched
    progress_status = models.CharField(max_length=10, default='incomplete')  # Can be 'incomplete' or 'complete'

    def __str__(self):
        return f"{self.user.username} - {self.course.course_name} - {self.progress_status}"



class Question(models.Model):
    course = models.ForeignKey(Course, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)  # True if this option is the correct answer

    def __str__(self):
        return self.text


from django.db import models

class QuizResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming you have a User model
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Option, on_delete=models.CASCADE)  # Link to the selected option
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.question.text} - {self.selected_answer.text}"
