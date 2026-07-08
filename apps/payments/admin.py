from django.contrib import admin
from .models import ZoomPayment, CoursePayment


@admin.register(ZoomPayment)
class ZoomPaymentAdmin(admin.ModelAdmin):
    list_display    = ('get_student', 'session', 'amount_paid', 'currency', 'payment_status', 'paid_at')
    list_filter     = ('payment_status', 'currency')
    search_fields   = ('student__email', 'payment_reference')
    readonly_fields = ('payment_reference', 'flutterwave_tx_id', 'created_at', 'paid_at')

    @admin.display(description='Student')
    def get_student(self, obj):
        return obj.student.get_full_name()


@admin.register(CoursePayment)
class CoursePaymentAdmin(admin.ModelAdmin):
    list_display    = ('get_student', 'course', 'amount_paid', 'currency', 'payment_status', 'paid_at')
    list_filter     = ('payment_status', 'currency')
    search_fields   = ('student__email', 'payment_reference')
    readonly_fields = ('payment_reference', 'flutterwave_tx_id', 'created_at', 'paid_at')

    @admin.display(description='Student')
    def get_student(self, obj):
        return obj.student.get_full_name()
