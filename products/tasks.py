from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from .models import CeleryTaskLog


@shared_task
def save_celery_log(message):
    log = CeleryTaskLog.objects.create(message=message)

    return f'Log {log.id} was saved'


@shared_task
def delete_old_logs():
    old_date = timezone.now() - timedelta(days=1)

    deleted_count, _ = CeleryTaskLog.objects.filter(
        created_at__lt=old_date
    ).delete()

    return f'Deleted {deleted_count} old logs'


@shared_task
def send_test_email(email):
    send_mail(
        subject='Celery SMTP test',
        message='This email was sent using Celery and SMTP.',
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )

    return f'Email sent to {email}'