from django.urls import path
from django.conf.urls.static import static
from CouserRecommendation import settings
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register_user', views.register_user, name='register_user'),
    path('login_user', views.login_user, name='login_user'),
    path('last-courses/', views.last_courses_view, name='last_courses'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/enroll/<int:course_id>/', views.enroll_student, name='enroll_student'),
    path('course/<int:id>/start_learning/', views.StartLearningView.as_view(), name='start_learning'),
    path('course/<int:course_id>/video/', views.VideoPlayerView.as_view(), name='video_player'),  # Video player page
    path('course/<int:course_id>/set_progress_complete/', views.VideoPlayerView.as_view(), name='set_progress_complete'),  # Progress tracking
    path('update_progress/<int:course_id>/', views.update_progress, name='update_progress'),
    path('get_user_progress/<int:course_id>/', views.get_user_progress, name='get_user_progress'),
    path('attend-quiz/<int:course_id>/', views.attend_quiz, name='attend_quiz'),
    path('review-quiz/', views.review_quiz, name='review_quiz'),
    path('certificate/<int:course_id>/', views.certificate_view, name='certificate_view'),
    path('edit-account/', views.edit_student_details, name='edit_student_details'),
    path('enrollments/', views.enrollments, name='enrollments'),
    path('get-courses/', views.get_courses, name='get_courses'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),

    path('about', views.about, name='about'),
    path('courses', views.courses, name='courses'),
    path('find', views.find, name='find'),
    path('contact', views.contact, name='contact'),
    path('profile', views.profile, name='profile'),
    path('user_logout', views.user_logout, name='user_logout'),



    #ADMIN
    path('admin_logout', views.admin_logout, name='admin_logout'),
    path('admin_index', views.admin_index, name='admin_index'),
    path('register-admin/', views.register_admin, name='register_admin'),
    path('login-admin/', views.login_admin, name='login_admin'),
    path('edit-profile/', views.edit_profile_admin, name='edit_profile_admin'),
    path('forms/', views.forms, name='forms'),
    path('add-category/', views.category_list, name='category_list'),
    path('edit-category/<int:pk>/', views.edit_category, name='edit_category'),
    path('delete-category/<int:pk>/', views.delete_category, name='delete_category'),
    path('add-course/', views.add_course, name='add_course'),
    path('courses/', views.course_list, name='course_list'),
    path('edit-course/<int:course_id>/', views.edit_course, name='edit_course'),
    path('delete-course/<int:course_id>/', views.delete_course, name='delete_course'),  
    path('add-questions/', views.add_questions, name='add_questions'),
    path('manage-quizzes/', views.manage_quizzes, name='manage_quizzes'),
    path('edit-question/<int:question_id>/', views.edit_question, name='edit_question'),
    path('delete-question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('registration-report/', views.registration_report, name='registration_report'),
    path('course-report/', views.course_report, name='course_report'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)