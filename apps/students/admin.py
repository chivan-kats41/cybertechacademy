"""
CyberTech Academy - Students Admin
Admit / Reject actions with email triggers.
"""
from django.contrib import admin, messages
from django.utils import timezone
from django.urls import reverse
from .models import StudentProfile, AdmissionPayment, Enrollment, LessonProgress
from apps.core.email_utils import send_admission_notification, send_rejection_email


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = (
        'get_full_name', 'get_email', 'admission_status',
        'admission_fee_paid', 'learning_mode', 'course_interest', 'date_registered',
    )
    list_filter   = ('admission_status', 'admission_fee_paid', 'learning_mode', 'is_active')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('date_registered', 'admitted_at', 'admission_fee_paid_at')
    ordering      = ('-date_registered',)
    actions       = ['admit_students', 'reject_students']

    fieldsets = (
        ('Student',   {'fields': ('user', 'course_interest', 'learning_mode', 'terms_accepted')}),
        ('Admission', {'fields': ('admission_status', 'admitted_at',
                                  'admission_fee_paid', 'admission_fee_paid_at',
                                  'admission_notes'), 'classes': ('wide',)}),
        ('Status',    {'fields': ('is_active', 'date_registered')}),
    )

    @admin.display(description='Student Name', ordering='user__first_name')
    def get_full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description='Email', ordering='user__email')
    def get_email(self, obj):
        return obj.user.email

    @admin.action(description='✅ Admit selected students & send payment link')
    def admit_students(self, request, queryset):
        admitted = skipped = 0
        for profile in queryset.select_related('user'):
            if profile.admission_status == StudentProfile.AdmissionStatus.ADMITTED:
                skipped += 1
                continue
            profile.admission_status = StudentProfile.AdmissionStatus.ADMITTED
            profile.admitted_at      = timezone.now()
            profile.user.is_active   = False   # stays locked until fee paid
            profile.user.save(update_fields=['is_active'])
            profile.save(update_fields=['admission_status', 'admitted_at'])
            payment_url = request.build_absolute_uri(reverse('students:admission_pay'))
            try:
                send_admission_notification(profile.user, payment_url)
            except Exception:
                pass
            admitted += 1
        if admitted:
            self.message_user(request,
                f"✅ {admitted} student(s) admitted — payment link email sent.", messages.SUCCESS)
        if skipped:
            self.message_user(request,
                f"⏭ {skipped} already admitted — skipped.", messages.WARNING)

    @admin.action(description='❌ Reject selected applications')
    def reject_students(self, request, queryset):
        rejected = 0
        for profile in queryset.select_related('user'):
            if profile.admission_status == StudentProfile.AdmissionStatus.REJECTED:
                continue
            profile.admission_status = StudentProfile.AdmissionStatus.REJECTED
            profile.user.is_active   = False
            profile.user.save(update_fields=['is_active'])
            profile.save(update_fields=['admission_status'])
            try:
                send_rejection_email(profile.user)
            except Exception:
                pass
            rejected += 1
        self.message_user(request, f"❌ {rejected} application(s) rejected.", messages.WARNING)


@admin.register(AdmissionPayment)
class AdmissionPaymentAdmin(admin.ModelAdmin):
    list_display    = ('get_student', 'amount', 'currency', 'payment_status', 'paid_at', 'created_at')
    list_filter     = ('payment_status', 'currency')
    search_fields   = ('student__email', 'student__first_name', 'payment_reference')
    readonly_fields = ('payment_reference', 'flutterwave_tx_id', 'created_at', 'paid_at')
    ordering        = ('-created_at',)

    @admin.display(description='Student')
    def get_student(self, obj):
        return f"{obj.student.get_full_name()} ({obj.student.email})"


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display  = ('student', 'course', 'enrolled_at', 'completed')
    list_filter   = ('completed', 'course')
    search_fields = ('student__email', 'course__title')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed', 'watched_at')
    list_filter  = ('completed',)