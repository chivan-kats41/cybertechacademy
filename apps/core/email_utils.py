"""
CyberTech Academy - Email Notification Utilities
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_registration_confirmation(user, course_name, learning_mode):
    """Send welcome email after student registers."""
    subject = "Welcome to CyberTech Academy! 🚀"
    context = {
        'user': user,
        'course_name': course_name,
        'learning_mode': learning_mode,
        'contact_phone_1': settings.CONTACT_PHONE_1,
        'contact_phone_2': settings.CONTACT_PHONE_2,
        'contact_email': settings.CONTACT_EMAIL,
        'dashboard_url': '/dashboard/',
    }
    html_message = render_to_string('emails/registration_confirmation.html', context)
    plain_message = render_to_string('emails/registration_confirmation.txt', context)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_zoom_access_email(user, session):
    """Send Zoom link after successful payment."""
    subject = f"✅ Your Zoom Session Access: {session.title}"
    context = {
        'user': user,
        'session': session,
        'contact_phone_1': settings.CONTACT_PHONE_1,
        'contact_email': settings.CONTACT_EMAIL,
    }
    html_message = render_to_string('emails/zoom_access.html', context)
    plain_message = render_to_string('emails/zoom_access.txt', context)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_payment_receipt(user, payment, item_name, amount, currency):
    """Generic payment receipt email."""
    subject = f"Payment Confirmed – {item_name}"
    context = {
        'user': user,
        'payment': payment,
        'item_name': item_name,
        'amount': amount,
        'currency': currency,
        'contact_email': settings.CONTACT_EMAIL,
    }
    html_message = render_to_string('emails/payment_receipt.html', context)
    plain_message = render_to_string('emails/payment_receipt.txt', context)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_admission_notification(user, payment_url):
    """Email sent when admin admits a student — includes payment link."""
    subject = "🎉 You've Been Admitted to CyberTech Academy!"
    context = {
        'user':             user,
        'payment_url':      payment_url,
        'admission_fee':    '20,000',
        'contact_phone_1':  settings.CONTACT_PHONE_1,
        'contact_phone_2':  settings.CONTACT_PHONE_2,
        'contact_email':    settings.CONTACT_EMAIL,
    }
    html_message  = render_to_string('emails/admission_notification.html', context)
    plain_message = render_to_string('emails/admission_notification.txt', context)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_admission_fee_confirmed(user):
    """Email sent once admission fee is verified."""
    subject = "✅ Admission Complete — Welcome to CyberTech Academy!"
    context = {
        'user':            user,
        'contact_phone_1': settings.CONTACT_PHONE_1,
        'contact_email':   settings.CONTACT_EMAIL,
    }
    html_message  = render_to_string('emails/admission_fee_confirmed.html', context)
    plain_message = render_to_string('emails/admission_fee_confirmed.txt', context)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_rejection_email(user, reason=''):
    """Email sent when admin rejects an application."""
    subject = "Update on Your CyberTech Academy Application"
    context = {
        'user':           user,
        'reason':         reason,
        'contact_phone_1': settings.CONTACT_PHONE_1,
        'contact_email':  settings.CONTACT_EMAIL,
    }
    html_message  = render_to_string('emails/admission_rejected.html', context)
    plain_message = render_to_string('emails/admission_rejected.txt', context)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )