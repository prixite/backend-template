from app import celery
from core.models import User


@celery.app.task
def send_verification_email(user_id):
    user = User.objects.get(id=user_id)
    user.send_verification_email()
