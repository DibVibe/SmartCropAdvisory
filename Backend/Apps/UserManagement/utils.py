import random
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


def generate_otp(length=6):
    """Generate random OTP"""
    return "".join(random.choices(string.digits, k=length))


def send_otp(phone_number, otp=None):
    """Send OTP via SMS"""
    if not otp:
        otp = generate_otp()

    # Store OTP in cache for 10 minutes
    cache_key = f"otp_{phone_number}"
    cache.set(cache_key, otp, 600)

    # Send SMS (placeholder - implement actual SMS service)
    try:
        # Example using SMS service API
        # response = requests.post(
        #     'https://sms-api.example.com/send',
        #     data={
        #         'to': phone_number,
        #         'message': f'Your SmartCropAdvisory OTP is: {otp}',
        #         'api_key': settings.SMS_API_KEY
        #     }
        # )
        # return response.status_code == 200

        logger.info(f"OTP {otp} sent to {phone_number}")
        return True

    except Exception as e:
        logger.error(f"Failed to send OTP: {e}")
        return False


def verify_otp(phone_number, otp):
    """Verify OTP"""
    cache_key = f"otp_{phone_number}"
    stored_otp = cache.get(cache_key)

    if stored_otp and stored_otp == otp:
        # Delete OTP after successful verification
        cache.delete(cache_key)
        return True

    return False


def send_notification(user, notification_type, title, message, channel="in_app"):
    """Send notification through various channels"""
    from .models import Notification

    # Create in-app notification
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        channel=channel,
        title=title,
        message=message,
    )

    # Send based on channel and user preferences
    if hasattr(user, "profile"):
        profile = user.profile

        if channel == "email" and profile.email_enabled:
            send_email_notification(user.email, title, message)

        elif channel == "sms" and profile.sms_enabled:
            send_sms_notification(profile.phone_number, message)

        elif channel == "push" and profile.device_token:
            send_push_notification(profile.device_token, title, message)

    return notification


def send_email_notification(email, subject, message):
    """Send email notification"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def send_sms_notification(phone_number, message):
    """Send SMS notification"""
    # Implement SMS sending logic
    logger.info(f"SMS to {phone_number}: {message}")
    return True


def send_push_notification(device_token, title, message):
    """Send push notification"""
    # Implement FCM/APNS push notification
    logger.info(f"Push notification to {device_token}: {title}")
    return True


def calculate_profile_completion(profile):
    """Calculate profile completion percentage"""
    required_fields = [
        "phone_number",
        "date_of_birth",
        "gender",
        "address_line1",
        "village",
        "district",
        "state",
        "pincode",
        "farm_size",
        "farming_experience",
        "education_level",
        "primary_crops",
    ]

    completed = 0
    for field in required_fields:
        value = getattr(profile, field, None)
        if value:
            if field == "primary_crops" and isinstance(value, list):
                if len(value) > 0:
                    completed += 1
            else:
                completed += 1

    return (completed / len(required_fields)) * 100
