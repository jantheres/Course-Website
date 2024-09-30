# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import QuizResponse
from datetime import timedelta

@shared_task
def delete_old_quiz_responses():
    threshold_time = timezone.now() - timedelta(hours=2)
    QuizResponse.objects.filter(created__lt=threshold_time).delete()
