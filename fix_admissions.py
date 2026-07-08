"""
CyberTech Academy — Fix Admission Records
Run once: python fix_admissions.py

This repairs students whose admission_status or admission_fee_paid
is wrong because they were seeded before the admission system existed,
or because a payment completed but the profile wasn't updated correctly.
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.utils import timezone
from apps.accounts.models import User
from apps.students.models import StudentProfile, AdmissionPayment

print("\n🔧 Fixing admission records...\n")

fixed = 0

for user in User.objects.filter(role='student'):
    try:
        profile = StudentProfile.objects.get(user=user)
    except StudentProfile.DoesNotExist:
        print(f"  ⚠️  {user.email} — no StudentProfile, skipping")
        continue

    changed = []

    # Case 1: Payment exists and is SUCCESS but profile not updated
    payment = AdmissionPayment.objects.filter(
        student=user, payment_status='success'
    ).first()

    if payment and not profile.admission_fee_paid:
        profile.admission_fee_paid    = True
        profile.admission_fee_paid_at = payment.paid_at or timezone.now()
        changed.append('admission_fee_paid=True (from successful payment)')

    if payment and profile.admission_status != StudentProfile.AdmissionStatus.ADMITTED:
        profile.admission_status = StudentProfile.AdmissionStatus.ADMITTED
        profile.admitted_at      = payment.paid_at or timezone.now()
        changed.append('admission_status=ADMITTED (from successful payment)')

    if payment and not user.is_active:
        user.is_active = True
        user.save(update_fields=['is_active'])
        changed.append('is_active=True')

    # Case 2: Seeded students (is_active=True but still pending) — auto-admit them
    if not payment and user.is_active and profile.admission_status == StudentProfile.AdmissionStatus.PENDING:
        profile.admission_status  = StudentProfile.AdmissionStatus.ADMITTED
        profile.admitted_at       = timezone.now()
        profile.admission_fee_paid    = True
        profile.admission_fee_paid_at = timezone.now()
        changed.append('auto-admitted (seeded student)')

    if changed:
        profile.save()
        fixed += 1
        print(f"  ✅  {user.email}")
        for c in changed:
            print(f"       → {c}")
    else:
        status = '✅ OK' if profile.can_login else '❌ blocked'
        print(f"  {status}  {user.email} (no changes needed)")

print(f"\n✅ Done — {fixed} student(s) repaired.\n")
print("Now run: python manage.py runserver")