from django.contrib import admin
from .models import Customer, Item, Quotation, QuotationItem, Invoice, Receipt


# Register your models here.
# Register your models here.
admin.site.site_header = 'Datos Management Information System'
admin.site.site_title = 'Datos Site Admin'
admin.site.index_title = 'Datos Administration'


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

# # Admin for Invoice
# @admin.register(Supplier)
# class SupplierAdmin(admin.ModelAdmin):
#     list_display = ('supplier_id', 'company_name','contact_name', 'phone', 'email', 'address')
#     search_fields = ('company_name',)
#     readonly_fields = ('supplier_id',)

    
# # Admin for Invoice
# @admin.register(Expense)
# class ExpenseAdmin(admin.ModelAdmin):
#     list_display = ('expense_id', 'name','description', 'company_name', 'amount')
#     list_filter = ('category_type', 'date', 'payment_method')
#     search_fields = ('expense_id',)
