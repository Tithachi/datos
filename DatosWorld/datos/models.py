from django.db import models
from django.utils import timezone
import random
from django.utils.safestring import mark_safe
from django.template.defaultfilters import truncatechars

class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    


class Quotation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField()
    items = models.ManyToManyField('Item', through='QuotationItem')
    quotation_number = models.CharField(max_length=8, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            self.quotation_number = self.generate_quotation_number()
        super().save(*args, **kwargs)

    def generate_quotation_number(self):
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        return f'DTS{random_digits}'

    def __str__(self):
        return self.quotation_number

class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()



class Invoice(models.Model):
    quotation = models.OneToOneField(Quotation, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=9, unique=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_updated = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Check if this is an update and store the old amount_paid
        if self.pk:
            old_invoice = Invoice.objects.get(pk=self.pk)
            old_amount_paid = old_invoice.amount_paid
        else:
            old_amount_paid = None

        # Update the invoice number if not present
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()

        # Call the original save method
        super().save(*args, **kwargs)

        # Create a receipt if this is a new invoice or if the amount_paid has changed
        if old_amount_paid is None:  # New invoice
            Receipt.objects.create(
                invoice=self,
                amount_received=self.amount_paid
            )
        elif self.amount_paid != old_amount_paid:  # Updated invoice with a new payment
            Receipt.objects.create(
                invoice=self,
                amount_received=self.amount_paid
            )

    def generate_invoice_number(self):
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        return f'DTSI{random_digits}'

    def __str__(self):
        return self.invoice_number



class Receipt(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='receipts')  # ForeignKey instead of OneToOneField
    receipt_number = models.CharField(max_length=9, unique=True, blank=True)
    date_received = models.DateTimeField(default=timezone.now)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Generate receipt number if not already set
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()

        super().save(*args, **kwargs)

    def generate_receipt_number(self):
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        return f'DTSR{random_digits}'

    def __str__(self):
        return f"Receipt {self.receipt_number} for Invoice {self.invoice.id}"


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
CATEGORY_TYPE1 = [
('Bank', 'Bank'),
('Accounts Recievable', 'Accounts Recievable'),
('Other Current Assets', 'Other Current Assets'),
('Fixed Asset', 'Fixed Asset'),
('Other Asset', 'Other Asset'),
('Other Current Liability', 'Other Current Liability'),
('Long Term Liability', 'Long Term Liability'),
('Equity', 'Equity'),
('Income', 'Income'),
('Cost of Goods Sold', 'Cost of Goods Sold'),
('Expenses', 'Expenses'),
('Other Income', 'Other Income'),
]    
class Category(models.Model):
  category_type = models.CharField(max_length=100,blank=True,null=True, choices=CATEGORY_TYPE1)
  category_name = models.CharField(max_length=100,blank=True,null=True)
  description = models.TextField(blank=True,null=True)

  class Meta:
            verbose_name_plural = 'Categories'

  @property
  def short_description(self):
         return truncatechars(self.description,70)

  def __str__(self):
        return self.category_name


# Supplier Model
class Supplier(models.Model):
    company_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company_name

# Expense Model
PAYMENT_METHOD = [
    ('Cash', 'Cash'),
    ('Card', 'Card'),
    ('Credit', 'Credit'),
    ('Airtel Money', 'Airtel Money'),
    ('MTN Money', 'MTN Money'),
    ('Other', 'Other')
]

CATEGORY_TYPE = [
    ('Bank Charge', 'Bank Charge'),
    ('Current Liabilities', 'Current Liabilities'),
    ('Long-Term Liabilities', 'Long-Term Liabilities'),
    ('Cost of Goods Sold', 'Cost of Goods Sold'),
    ('Operating Expenses', 'Operating Expenses'),
    ('Administrative Expenses', 'Administrative Expenses'),
    ('Marketing Expenses', 'Marketing Expenses'),
    ('Depreciation', 'Depreciation'),
    ('Miscellaneous Expenses', 'Miscellaneous Expenses'),
]

class Expense(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category_type = models.CharField(max_length=50, choices=CATEGORY_TYPE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.supplier.company_name}"
