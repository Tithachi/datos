from django.contrib import admin
from .models import Customer, Item, Quotation, QuotationItem, Invoice, Receipt, Expense, Supplier, Bank, KPI, Task, Reminder, Profile
from django.utils.html import format_html  # Import format_html


# Register your models here.
# Register your models here.
admin.site.site_header = 'Datos Management Information System'
admin.site.site_title = 'Datos Site Admin'
admin.site.index_title = 'Datos Administration'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'phone_number', 'city', 'country')
    list_filter = ('city', 'country', 'user')
    search_fields = ('user__username', 'phone_number', 'city', 'country')
    readonly_fields = ('profile_photo_preview',)

    def profile_photo_preview(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" style="width: 50px; height:50px;" />'.format(obj.profile_photo.url))
        return "No Image"
    profile_photo_preview.short_description = 'Profile Photo Preview'

    fieldsets = (
        (None, {
            'fields': ('user', 'bio', 'profile_photo', 'profile_photo_preview')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address', 'city', 'state', 'postal_code', 'country')
        }),
    )


# Inline model admin for QuotationItem
class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1

# Admin for Quotation
@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('quotation_number', 'customer', 'date_created', 'expiry_date')
    list_filter = ('date_created', 'expiry_date')
    inlines = [QuotationItemInline]
    readonly_fields = ('quotation_number',)
    search_fields = ('quotation_number','date_created')

    def save_model(self, request, obj, form, change):
        # Generate quotation number if it doesn't already exist
        if not obj.quotation_number:
            obj.quotation_number = obj.generate_quotation_number()
        super().save_model(request, obj, form, change)

# Admin for Invoice
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('quotation', 'invoice_number','date_created', 'due_date', 'date_updated', 'amount_paid')
    list_filter = ('date_created', 'due_date')
    search_fields = ('invoice_number',)
    readonly_fields = ('invoice_number', 'date_updated')

# Admin for Receipt
@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'invoice', 'date_received', 'amount_received')
    list_filter = ('date_received',)

# Admin for Customer
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name','company', 'email', 'phone','address')
    search_fields = ('name', 'email','phone','company')

# Admin for Item
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description','unit_price')
    search_fields = ('name',)

# Admin for Invoice
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('company_name','contact_name', 'phone', 'email', 'address')
    search_fields = ('company_name',)

    
# Admin for Invoice
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('name','description', 'supplier', 'amount')
    list_filter = ('category_type', 'date', 'payment_method')
    search_fields = ('date',)


# Admin for Bank model
@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'swift_code')
    search_fields = ('name', 'swift_code')

# Admin for Task model
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'progress', 'risk_level', 'kpi', 'due_date')
    list_filter = ('risk_level', 'due_date', 'kpi')

# Admin for KPI model
@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'workstream')
    list_filter = ('workstream',)
    search_fields = ('name',)


# Admin for Reminder
@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('task', 'reminder_date', 'message')
    list_filter = ('reminder_date',)
    search_fields = ('task__task_name',)