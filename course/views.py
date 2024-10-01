import json
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views import View
from .forms import StudentRegistrationForm
from .models import QuizResponse, Student
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.shortcuts import redirect
from django.urls import reverse

def login_required_user(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login_user'))  # Replace with your login URL
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


User = get_user_model()  # Get the custom user model

def login_required_admin(view_func):
    @login_required  # Use the built-in login_required decorator first
    def _wrapped_view(request, *args, **kwargs):
        if isinstance(request.user, User) and request.user.is_staff:  # Check if the user is an admin
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('login_admin'))  # Redirect to login if not an admin
    return _wrapped_view

def register_user(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # Attempt to create a user instance
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],  # Use email as username
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                # Create a Student instance linked to the user
                student = form.save(commit=False)
                student.user = user  # Assign the user instance to the student
                student.password = make_password(form.cleaned_data['password'])  # Hash the password
                student.save()
                messages.success(request, "Registration successful!")  # Show success message
                return redirect('login_user')  # Redirect to login page after successful registration
            except IntegrityError:
                form.add_error('email', 'This email address is already registered.')  # Add error to the form
    else:
        form = StudentRegistrationForm()

    return render(request, 'register_user.html', {'form': form})



from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Redirect to a home page or dashboard after login
        else:
            error_message = "Invalid username or password."
            return render(request, 'login_user.html', {'error_message': error_message})

    return render(request, 'login_user.html')



from django.shortcuts import redirect
from django.contrib.auth import logout


def user_logout(request):
    logout(request)
    return redirect('index') 

from django.shortcuts import render
from .models import Course

def last_courses_view(request):
    courses = Course.objects.order_by('-created_at')[:4]  # Fetch the last 4 courses
    return render(request, 'your_template.html', {'courses': courses})

from django.shortcuts import render
from .models import Category  # Adjust the import based on your project structure

def category_last(request):
    # Fetch the last 8 categories
    categories = Category.objects.order_by('-id')[:8]
    context = {
        'categories': categories,
    }
    return render(request, 'your_template.html', context)

import random
from django.shortcuts import render
from .models import Course, Category  # Adjust based on your project structure

def index(request):
    # Fetch the last 4 courses
    courses = Course.objects.order_by('-created_at')[:4]
    
    # Fetch the last 8 categories
    categories = Category.objects.order_by('id')[:9]
    
    # List of image paths
    images = [
        'assets/img/gallery/featured1.png',
        'assets/img/gallery/featured2.png',
        'assets/img/gallery/featured3.png',
        'assets/img/gallery/featured4.png',
        # Add more images as needed
    ]

    # Shuffle the images and select up to 4 unique images
    random.shuffle(images)
    selected_images = images[:4]  # Select the first 4 images from the shuffled list

    context = {
        'courses': courses,
        'categories': categories,
        'selected_images': selected_images,  # Add selected images to context
    }
    return render(request, 'index.html', context)  # Ensure to use your actual index template name

from .models import Category  # Ensure Category model is imported

def about(request):
    # Fetch the last 9 categories
    categories = Category.objects.order_by('id')[:9]
    
    context = {
        'categories': categories
    }
    
    return render(request, 'about.html', context)  # Ensure the correct template is rendered





from django.shortcuts import render
from .models import Course, Category

def courses(request):
    # Fetch all categories for the dropdown
    categories = Category.objects.all()
    
    # Start with all courses
    courses = Course.objects.all()  

    # Get the selected category from the query parameters
    selected_category_id = request.GET.get('category')
    print(f'Selected Category ID: {selected_category_id}')  # Debugging output

    # Filter by selected category if one is chosen
    if selected_category_id:
        try:
            # Ensure it’s an integer
            selected_category_id = int(selected_category_id)  
            courses = courses.filter(category_id=selected_category_id)
            print(f'Filtered Courses: {[course.course_name for course in courses]}')  # Debugging output
        except (ValueError, TypeError):
            print(f'Invalid category ID: {selected_category_id}')  # Debugging output

    # Handle the search query if provided
    search_query = request.GET.get('search', '')  # Default to an empty string
    if search_query:
        # Apply search across course name and description
        courses = courses.filter(course_name__icontains=search_query) | courses.filter(description__icontains=search_query)

    context = {
        'courses': courses,  # Pass the filtered or unfiltered courses
        'categories': categories,  # Pass all categories for the dropdown
        'selected_category_id': selected_category_id,  # Pass selected category to the template
        'search_query': search_query,  # Pass the search query to the template
    }

    return render(request, 'courses.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment
from django.contrib.auth.decorators import login_required

@login_required_user
def course_detail(request, course_id):
    # Retrieve the course based on the provided course_id
    course = get_object_or_404(Course, id=course_id)
    
    # Extract the duration in hours and minutes
    duration_hours = course.duration.hour
    duration_minutes = course.duration.minute

    # Check if the user is enrolled in the course
    student = get_object_or_404(Student, user=request.user)
    enrolled = Enrollment.objects.filter(student=student, course=course).exists()

    # Render the template with the course details, duration, and enrollment status
    return render(request, 'course_detail.html', {
        'course': course,
        'duration_hours': duration_hours,
        'duration_minutes': duration_minutes,
        'enrolled': enrolled,  # Pass enrollment status
    })


@login_required_user
def enroll_student(request, course_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        course = get_object_or_404(Course, id=course_id)

        # Create an enrollment
        enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)
        
        if created:
            return redirect('course_detail', course_id=course_id)  # Redirect to course detail page
        else:
            # If already enrolled, you can show a message or handle it accordingly
            return render(request, 'course_detail.html', {
                'course': course,
                'duration_hours': course.duration.hour,
                'duration_minutes': course.duration.minute,
                'enrolled': True,
                'message': "You are already enrolled in this course."
            })


from django.shortcuts import render, get_object_or_404
from .models import Course

class StartLearningView(View):
    def get(self, request, id):
        course = get_object_or_404(Course, id=id)
        
        # Collecting available modules into a list
        modules = [course.module_1, course.module_2, course.module_3, course.module_4, 
                   course.module_5, course.module_6, course.module_7, course.module_8, 
                   course.module_9, course.module_10]
        available_modules = [module for module in modules if module]  # Filter out empty modules

        context = {
            'course': course,
            'available_modules': available_modules,
        }
        return render(request, 'start_learning.html', context)



from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views import View
from .models import Course, UserProgress
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

# Function to convert shareable link to embed link (for YouTube-like platforms)
def convert_to_embed(link):
    if 'youtube.com' in link or 'youtu.be' in link:
        # Convert YouTube links to embedded format
        if 'watch?v=' in link:
            return link.replace('watch?v=', 'embed/')
        elif 'youtu.be/' in link:
            return link.replace('youtu.be/', 'youtube.com/embed/')
    # You can add more platform-specific conversion logic if needed
    return link  # Return the original link if no conversion is needed

from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views import View
from .models import Course, UserProgress
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

class VideoPlayerView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        # Collect all non-empty module links
        video_links = [
            convert_to_embed(getattr(course, f'module_{i}', None))
            for i in range(1, 11) if getattr(course, f'module_{i}', None)
        ]

        # Get the user's progress
        user_progress = UserProgress.objects.filter(user=request.user, course=course).first()
        current_video_index = user_progress.current_video_index if user_progress else 0

        # Set context
        context = {
            'course': course,
            'embed_links': video_links,
            'current_video_index': current_video_index
        }
        return render(request, 'video_player.html', context)

    @method_decorator(csrf_exempt)
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        user_progress, created = UserProgress.objects.get_or_create(user=request.user, course=course)

        data = json.loads(request.body)
        current_video_index = data.get('current_video_index')

        # Update user progress
        user_progress.current_video_index = current_video_index

        # Check if the last video has been watched
        if current_video_index >= len([link for link in [getattr(course, f'module_{i}', None) for i in range(1, 11)] if link]):
            user_progress.progress_status = 'complete'
        else:
            user_progress.progress_status = 'incomplete'

        user_progress.save()
        return JsonResponse({'status': 'success'})


from django.http import JsonResponse
from .models import UserProgress  # Assuming you have a model to store user progress

def get_user_progress(request, course_id):
    if request.method == 'GET':
        user_progress = UserProgress.objects.filter(user=request.user, course_id=course_id).first()
        current_video_index = user_progress.current_video_index if user_progress else 0
        return JsonResponse({'current_video_index': current_video_index})


from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def update_progress(request, course_id):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        completed_videos = data.get('current_video_index') + 1  # Increment because index starts from 0
        
        # Get or create course progress for the user
        user_progress, created = CourseProgress.objects.get_or_create(user=request.user, course_id=course_id)
        user_progress.completed_videos = completed_videos
        
        # Check if course is complete
        if completed_videos >= data.get('total_videos'):
            user_progress.is_complete = True
        
        user_progress.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})



@login_required_user
def attend_quiz(request, course_id):
    if request.method == 'POST':
        user = request.user  
        
        # Delete previous responses for this user and course
        QuizResponse.objects.filter(user=user, question__course_id=course_id).delete()
        
        total_marks = 0  # Initialize total marks
        total_questions = Question.objects.filter(course_id=course_id).count()  # Total number of questions
        
        # Process each question for the given course
        for question in Question.objects.filter(course_id=course_id):
            selected_option_text = request.POST.get(f'answers_{question.id}')
            selected_option = Option.objects.filter(text=selected_option_text, question=question).first()

            if selected_option:
                # Determine if the answer is correct
                is_correct = selected_option.is_correct
                
                # Save the response
                QuizResponse.objects.create(
                    user=user,
                    question=question,
                    selected_answer=selected_option,
                    is_correct=is_correct
                )
                
                # Increment total marks if the answer is correct
                if is_correct:
                    total_marks += 1  # Assuming 1 mark for each correct answer
        
        # Store the total marks in the session or pass to the template
        request.session['total_marks'] = total_marks
        request.session['total_questions'] = total_questions

        return redirect('review_quiz')  # Redirect to the review page
        
    else:
        # Render the quiz form
        questions = Question.objects.filter(course_id=course_id)  # Fetch questions based on the course
        return render(request, 'attend_quiz.html', {'questions': questions, 'course_id': course_id})



from django.shortcuts import render
from .models import QuizResponse, Option
@login_required_user
def review_quiz(request):
    # Get all quiz responses for the user
    responses = QuizResponse.objects.filter(user=request.user)

    # Check if there are any responses to get the course_id
    if responses.exists():
        # Assuming each response is linked to a question, and the question is linked to a course
        course_id = responses.first().question.course.id  # Adjust this if your model differs
    else:
        course_id = None

    # Prepare data to pass to the template
    review_data = []
    total_marks = 0  # Initialize total marks
    total_questions = responses.count()  # Total questions is the count of responses

    for response in responses:
        correct_answer = response.question.options.filter(is_correct=True).first()
        review_data.append({
            'question': response.question,
            'selected_answer': response.selected_answer,
            'correct_answer': correct_answer,
        })

        # Increment total_marks if the selected answer is correct
        if response.selected_answer == correct_answer:
            total_marks += 1

    # Calculate percentage
    percentage = (total_marks / total_questions * 100) if total_questions else 0

    # Pass all necessary data to the template
    return render(request, 'review_quiz.html', {
        'review_data': review_data,
        'total_marks': total_marks,
        'total_questions': total_questions,
        'percentage': percentage,
        'course_id': course_id,  # Pass course_id to the template
    })



from django.http import JsonResponse
from .models import CourseProgress

def get_user_progress(request, course_id):
    if request.user.is_authenticated:
        user_progress, created = CourseProgress.objects.get_or_create(user=request.user, course_id=course_id)
        return JsonResponse({
            'completed_videos': user_progress.completed_videos,
            'is_complete': user_progress.is_complete
        })
    return JsonResponse({'completed_videos': 0, 'is_complete': False})



def find(request):
    return render(request, 'find.html')
def contact(request):
    return render(request, 'contact.html')


def profile(request):
    return render(request, 'profile.html')




#ADMIN


def admin_logout(request):
    logout(request)
    return redirect('index')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from .models import Student, Course, Enrollment, UserProgress, Category  # Include Category model
from datetime import datetime

@login_required_admin
def admin_index(request):
    # Get the current year
    current_year = datetime.now().year

    # Query to count student registrations per month
    monthly_registrations = (
        Student.objects.filter(created_on__year=current_year)
        .annotate(month=TruncMonth('created_on'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Prepare a dictionary to hold registration counts for each month
    month_dict = {month: 0 for month in range(1, 13)}  # Pre-fill with 0 for all 12 months

    # Update the month_dict with actual data from the query
    for registration in monthly_registrations:
        month_dict[registration['month'].month] = registration['count']

    # Prepare labels (month names) and data (registration counts)
    labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data = [month_dict[month] for month in range(1, 13)]  # Get the count for each month

    # New Query to count enrollments for each course
    course_enrollments = (
        Enrollment.objects.values('course__course_name')
        .annotate(enrollment_count=Count('id'))
    )

    # Prepare labels and data for the donut chart
    course_labels = [entry['course__course_name'] for entry in course_enrollments]
    course_data = [entry['enrollment_count'] for entry in course_enrollments]

    # New query to fetch student progress (videos watched per month)
    progress_data = [0] * 12  # Initialize an array to hold progress data for each month
    user_progresses = (
        UserProgress.objects.filter(course__isnull=False)  # Ensure there's a related course
        .annotate(month=TruncMonth('user__student__created_on'))  # Assuming UserProgress links to Student through User
        .values('month')
        .annotate(total_videos_watched=Sum('current_video_index'))  # Sum the current video index
        .order_by('month')
    )

    # Populate progress_data with actual progress
    for progress in user_progresses:
        month = progress['month'].month  # Get the month
        progress_data[month - 1] = progress['total_videos_watched']  # Subtract 1 for zero-indexing

    # Query to get the last 5 categories
    categories = Category.objects.order_by('-id')[:5]  # Fetch last 5 categories by descending order of ID
    last_courses = Course.objects.order_by('-id')[:5]  # Fetch last 5 courses by descending order of ID
    last_students = Student.objects.order_by('-id')[:5]  # Fetch last 5 courses by descending order of ID

    # Pass the data to the template
    context = {
        'labels': labels,
        'data': data,
        'course_labels': course_labels,  # Pass course labels for the donut chart
        'course_data': course_data,  # Pass course enrollment data for the donut chart
        'progress_data': progress_data,  # Pass progress data for the line chart
        'categories': categories,  # Pass categories to the template
        'last_courses': last_courses,
        'last_students': last_students,
    }
    return render(request, 'admin/index.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Admin
from django.contrib import messages

# View to register Admin data
def register_admin(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Create a new User
        user = User.objects.create_user(username=username, password=password, email=email)

        # Create an Admin profile and associate it with the User
        admin = Admin.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            username=username,
            password=make_password(password)  # Ensures password is hashed
        )

        # Redirect to a success page or admin list page
        messages.success(request, "Admin successfully registered!")
        return redirect('index')

    # If GET request, show the form
    return render(request, 'admin/register_admin.html')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

# Admin login view
def login_admin(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Log the user in and redirect to the dashboard
            login(request, user)
            return redirect('admin_index')  # You can change this to your admin dashboard URL
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login_admin')  # Redirect to login page with error message
    
    # If GET request, render the login page
    return render(request, 'admin/login_admin.html')


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Admin  # Assuming your Admin model is in the same app

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()  # Get the user model (custom or default)

@login_required_admin  # Ensure only logged-in admins can access this view
def edit_profile_admin(request):
    user = request.user  # Get the currently logged-in user (admin)

    if request.method == 'POST':
        # Update user details
        user.username = request.POST.get('username', user.username)  # Update username if provided
        user.email = request.POST.get('email', user.email)  # Update email if provided
        
        try:
            user.save()  # Save the updated user details
            messages.success(request, 'Profile updated successfully!')
            return redirect('edit_profile_admin')  # Redirect to the same page after successful update
        except Exception as e:
            messages.error(request, f'Error updating profile: {e}')

    return render(request, 'admin/edit_profile_admin.html', {'admin': user})  # Render the edit form


def forms(request):
    return render(request, 'admin/forms.html')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Category
from .forms import CategoryForm

@login_required_admin
def category_list(request):
    categories = Category.objects.all()  # Get all categories

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new category
            return redirect('category_list')  # Redirect to the category list page
    else:
        form = CategoryForm()

    return render(request, 'admin/category_list.html', {
        'categories': categories,
        'form': form,
    })


@login_required_admin
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)  # Get the specific category
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()  # Save the edited category
            return redirect('category_list')  # Redirect to the category list page
    else:
        form = CategoryForm(instance=category)

    return render(request, 'admin/edit_category.html', {
        'form': form,
        'category': category,
    })


@login_required_admin
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()  # Delete the category
    return redirect('category_list')  # Redirect to the category list page


from django.shortcuts import render, redirect
from .models import Course, Category
from .forms import CourseForm

@login_required_admin
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)

            # Handling dynamically added module fields manually
            for i in range(3, 11):  # Modules 3 to 10
                module_url = request.POST.get(f'module_{i}')
                if module_url:
                    setattr(course, f'module_{i}', module_url)
            
            course.save()
            return redirect('course_list')
    else:
        form = CourseForm()

    categories = Category.objects.all()
    return render(request, 'admin/add_course.html', {'form': form, 'categories': categories})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Category
from .forms import CourseForm

@login_required_admin
def course_list(request):
    courses = Course.objects.all()  # Get all courses
    return render(request, 'admin/course_list.html', {'courses': courses})


from django.shortcuts import get_object_or_404, redirect, render
from .models import Course, Category
from .forms import EditCourseForm  # Import the new form

@login_required_admin
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Convert duration to hours and minutes
    duration_hours = course.duration.hour
    duration_minutes = course.duration.minute

    if request.method == 'POST':
        form = EditCourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()  # Save the updated course details
            return redirect('course_list')  # Redirect after saving
    else:
        form = EditCourseForm(instance=course)

    categories = Category.objects.all()  # Fetch categories for the dropdown
    return render(request, 'admin/edit_course.html', {
        'form': form,
        'categories': categories,
        'course': course,
        'duration_hours': duration_hours,  # Pass hours separately
        'duration_minutes': duration_minutes,  # Pass minutes separately
    })


from django.shortcuts import render, redirect, get_object_or_404
from .models import Course

@login_required_admin
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()  # Delete the course
    return redirect('course_list')  # Redirect back to the course list after deletion



from django.shortcuts import render, redirect
from .models import Course, Question, Option

@login_required_admin
def add_questions(request):
    if request.method == 'POST':
        course_id = request.POST.get('course')
        question_text = request.POST.get('question_text')
        options = request.POST.getlist('options')
        correct_option_index = request.POST.get('correct_option')  # Get index of the correct option

        # Check the number of questions already associated with the course
        if Question.objects.filter(course_id=course_id).count() < 10:
            # Create Question
            question = Question.objects.create(course_id=course_id, text=question_text)

            # Add options
            for i, option_text in enumerate(options):
                is_correct = (str(i + 1) == correct_option_index)  # Check if this option is correct
                Option.objects.create(question=question, text=option_text, is_correct=is_correct)

            return redirect('add_questions')  # Redirect after POST
        else:
            return render(request, 'admin/add_questions.html', {
                'courses': Course.objects.all(),
                'error': 'A course can only have up to 10 questions.'  # Show error message if limit reached
            })
    else:
        courses = Course.objects.all()
        return render(request, 'admin/add_questions.html', {'courses': courses})


from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, Question, Option

@login_required_admin
def manage_quizzes(request):
    courses = Course.objects.all()
    selected_course = None
    questions = []

    if request.method == 'POST':
        selected_course = request.POST.get('course')
        questions = Question.objects.filter(course_id=selected_course)

    return render(request, 'admin/manage_quizzes.html', {
        'courses': courses,
        'selected_course': selected_course,
        'questions': questions,
    })

from django.shortcuts import get_object_or_404

@login_required_admin
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    options = question.options.all()  # Get existing options

    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        option_texts = request.POST.getlist('options')  # Get all options from the form
        correct_option_text = request.POST.get('correct_option')

        # Update the question text
        question.text = question_text
        question.save()

        # Update options
        for i, option in enumerate(options):
            option.text = option_texts[i]
            option.is_correct = (option.text == correct_option_text)
            option.save()

        # Check if new options need to be added
        for option_text in option_texts[len(options):]:
            Option.objects.create(question=question, text=option_text, is_correct=(option_text == correct_option_text))

        return redirect('manage_quizzes')  # Redirect after saving changes

    return render(request, 'admin/edit_question.html', {'question': question, 'options': options})


def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        question.delete()
        return redirect('manage_quizzes')
    return render(request, 'admin/delete_question.html', {'question': question})




from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
@login_required_user
def download_certificate(request):
    user = request.user  # Assuming the user is authenticated and their data is used.
    course = {
        "course_name": "Your Course Name",
        "duration": "40 hours"
    }

    # Prepare the context data
    context = {
        'user': user,
        'course': course,
        'date': datetime.now()  # Pass the current date to the template
    }

    # Render the certificate HTML
    html_string = render(request, 'certificate.html', context).content.decode()

    # Create a CSS stylesheet for the PDF
    pdf_css = CSS(string='@page { size: A4 landscape; margin: 1cm; }')  # Landscape A4 with margins

    # Convert HTML to PDF
    pdf_file = HTML(string=html_string).write_pdf(stylesheets=[pdf_css])

    # Return PDF as a download response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'
    
    return response

from django.shortcuts import render, get_object_or_404
from .models import Student, Course, CourseProgress
@login_required_user
def certificate_view(request, course_id):
    # Get the logged-in student
    student = request.user.student

    # Check the course progress for the specific course
    course_progress = get_object_or_404(CourseProgress, user=request.user, course_id=course_id)

    # Check if the course is completed
    if not course_progress.is_complete:
        # If the course is not complete, return an error or redirect
        return render(request, 'not_completed.html')  # You can create a separate page for incomplete courses

    # Fetch the course details
    course = get_object_or_404(Course, id=course_id)

    # Pass the user, course, and course progress details to the template
    context = {
        'user': student,         # The student (related to the logged-in user)
        'course': course,        # The course they completed
        'course_progress': course_progress,  # Additional course progress data if needed
    }

    return render(request, 'certificate.html', context)


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EditStudentForm  # Import the form
from django.contrib.auth.models import User

@login_required_user
def edit_student_details(request):
    user = request.user  # Get the currently logged-in user
    student = user.student  # Get the user's student profile

    if request.method == 'POST':
        form = EditStudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            user.username = request.POST['username']  # Update username
            user.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('edit_student_details')
    else:
        form = EditStudentForm(instance=student)

    context = {
        'form': form,
        'admin': user,  # Pass the user object to the template
    }

    return render(request, 'edit_student.html', context)



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Enrollment, CourseProgress

@login_required_user
def enrollments(request):
    # Get the current logged-in student (assuming there is a related Student model)
    student = request.user.student

    # Get all the courses the student is enrolled in
    enrolled_courses = Enrollment.objects.filter(student=student)

    # Get the progress for each course
    progress = CourseProgress.objects.filter(user=request.user)

    # Prepare the data to pass to the template
    enrollment_data = []
    for enrollment in enrolled_courses:
        # Find the progress for the specific course (if exists)
        course_progress = progress.filter(course_id=enrollment.course.id).first()
        enrollment_data.append({
            'course': enrollment.course,
            'enrollment_date': enrollment.enrollment_date,
            'completed_videos': course_progress.completed_videos if course_progress else 0,
            'is_complete': course_progress.is_complete if course_progress else False,
        })

    context = {
        'enrollment_data': enrollment_data,
    }

    return render(request, 'enrollments.html', context)

# Additional logic to handle downloading certificates or continuing courses can be added in other views
@login_required_user
def download_certificate(request, course_id):
    # Logic to generate and download certificate for the completed course
    # Can use something like a PDF library to generate the certificate dynamically
    pass

@login_required_user
def continue_course(request, course_id):
    # Logic to direct the user to the course module to continue
    return redirect(f'/courses/{course_id}')  # Example redirect to the course page



import os
import google.generativeai as genai
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

# Configure the API key
genai.configure(api_key=settings.GEMINI_API_KEY)

def clean_text(text):
    cleaned = text.replace('*', '').replace('#', '').strip()
    return cleaned

def process_data(data):
    result = []
    current_course = {}
    existing_links = set()  # For duplicate checking

    for line in data.splitlines():
        cleaned_line = clean_text(line)

        if 'Course Name:' in cleaned_line:
            if current_course:  
                if current_course['link'] not in existing_links:  # Check for duplicates
                    result.append(current_course)
                    existing_links.add(current_course['link'])
                current_course = {}  
            current_course['title'] = cleaned_line.split('Course Name:')[1].strip()

        elif 'Provider:' in cleaned_line:
            current_course['provider'] = cleaned_line.split('Provider:')[1].strip()

        elif 'Rating:' in cleaned_line:
            current_course['rating'] = cleaned_line.split('Rating:')[1].strip()

        elif 'Description:' in cleaned_line:
            current_course['description'] = cleaned_line.split('Description:')[1].strip()

        elif 'Link:' in cleaned_line:
            link = cleaned_line.split('Link:')[1].strip().lstrip('[').split(']')[0].strip()
            current_course['link'] = link

    if current_course and current_course['link'] not in existing_links:
        result.append(current_course)

    return result
@login_required_user
def get_courses(request):
    # If this is a POST request, process the form data
    if request.method == "POST":
        interests = request.POST.get("interests")
        
        # Define the prompt template with user's interests
        prompt = f"My interests are {interests}."

        # API configuration for generation
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        # Create the model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        # Start the chat session with the model
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        "Please find online courses based on my interests. I am interested in {{interests}}. I would like to receive at least 10 results formatted as follows: Course name: <Course Title> (next line) Provider: <Provider Name> (next line) Rating: <Rating> (next line) Description: <Description> (next line) Link: <Link>. Ensure that Course Title is mandatory. First, show courses that include all my interests in one course. Then, show courses that match any of my interests. If no courses are found that meet the criteria, please respond with: 'No courses found for the specific interests combined.' Make sure that each link is provided only once for each course.",
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "Please provide me with your interests so I can find relevant online courses for you! 😊 \n",
                    ],
                },
            ]
        )

        try:
            # Send the message with the user's interests
            response = chat_session.send_message(prompt)

            # Extract the results and process data
            courses_data = process_data(response.text)

            # Render the response in the template
            return render(request, "courses_result.html", {"courses_data": courses_data})
        except Exception as e:
            # Handle the error appropriately
            print(f"Error occurred: {e}")
            return render(request, "courses_result.html", {"courses_data": None})

    # If not a POST request, display the form
    return render(request, "courses_form.html")



from django.shortcuts import render
from .models import Student
@login_required_admin
def student_list(request):
    students = Student.objects.all()  # Fetch all Student records
    context = {
        'students': students,
    }
    return render(request, 'admin/student_list.html', context)



from django.shortcuts import render, get_object_or_404
from .models import Student, Enrollment, Course, CourseProgress
from django.contrib.auth.decorators import login_required

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)  # Get the student by ID
    enrollments = Enrollment.objects.filter(student=student)  # Get all enrollments for this student

    # Get the User object associated with the student
    user = student.user  
    # Count completed courses using the CourseProgress model
    completed_courses_count = CourseProgress.objects.filter(user=user, is_complete=True).count()  

    context = {
        'student': student,
        'enrollments': enrollments,
        'completed_courses_count': completed_courses_count,
    }
    return render(request, 'admin/student_detail.html', context)


from django.shortcuts import render
from .models import Student
from .forms import RegistrationReportForm
from django.db.models import Q

def registration_report(request):
    form = RegistrationReportForm()
    students = None

    if request.method == 'POST':
        form = RegistrationReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Query to get students registered within the date range
            students = Student.objects.filter(created_on__range=(start_date, end_date))

    context = {
        'form': form,
        'students': students,
    }
    return render(request, 'admin/registration_report.html', context)


# views.py
from django.shortcuts import render
from .models import Course, Enrollment

def course_report(request):
    courses = Course.objects.all()  # Fetch all available courses
    students = []
    selected_course_name = ""

    if request.method == "POST":
        selected_course_id = request.POST.get('course')  # Get selected course ID
        if selected_course_id:
            # Filter enrollments based on the selected course
            enrollments = Enrollment.objects.filter(course__id=selected_course_id)
            students = [enrollment.student for enrollment in enrollments]  # Extract students
            selected_course_name = Course.objects.get(id=selected_course_id).course_name

    context = {
        'courses': courses,
        'students': students,
        'selected_course_name': selected_course_name,
    }
    return render(request, 'admin/course_report.html', context)







# views.py
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from .forms import ForgotPasswordForm
from .models import Student

def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                student = Student.objects.get(email=email)
                user = student.user

                # Generate token and uid
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Create password reset URL
                reset_url = request.build_absolute_uri(
                    reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
                )

                # Send email
                subject = 'Password Reset Request'
                message = render_to_string('email_reset_password.html', {
                    'user': user,
                    'reset_url': reset_url
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

                return render(request, 'forgot_password_done.html')

            except Student.DoesNotExist:
                form.add_error('email', 'Email does not exist')
    else:
        form = ForgotPasswordForm()

    return render(request, 'forgot_password.html', {'form': form})




# views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

def reset_password(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                return redirect('password_reset_complete')
            else:
                return render(request, 'reset_password.html', {
                    'error': 'Passwords do not match',
                    'uidb64': uidb64,
                    'token': token
                })
        return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})
    else:
        return render(request, 'reset_password_invalid.html')


# views.py
from django.shortcuts import render

def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')



