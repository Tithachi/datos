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
    
    

class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=150)
    contact_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=13)
    email = models.EmailField(null=True,blank=True)
    address = models.TextField()

    class Meta:
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return self.company_name


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
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)

    def generate_invoice_number(self):
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        return f'DTSI{random_digits}'

    def __str__(self):
        return self.invoice_number

class Receipt(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    date_received = models.DateTimeField(default=timezone.now)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Receipt {self.id} for Invoice {self.invoice.id}"

class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
CATEGORY_TYPE = [
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
  category_type = models.CharField(max_length=100,blank=True,null=True, choices=CATEGORY_TYPE)
  category_name = models.CharField(max_length=100,blank=True,null=True)
  description = models.TextField(blank=True,null=True)

  class Meta:
            verbose_name_plural = 'Categories'

  @property
  def short_description(self):
         return truncatechars(self.description,70)

  def __str__(self):
        return self.category_name


PAYMENT_METHOD = [
('Cash', 'Cash'),
('Card', 'Card'),
('Credit', 'Credit'),
('Airtel Money', 'Airtel Money'),
('MTN Money', 'MTN Money'),
('Other', 'Other')
]


class Expense(models.Model):
    # receipt_photo = models.ImageField(null=True,blank=True, upload_to="images/")
    expense_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True,null=True)
    company_name = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True,blank=True)
    category_type = models.CharField(max_length=100,blank=True,null=True, choices=CATEGORY_TYPE)
    date = models.DateField(null=True,blank=True)
    amount = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD,null=True,blank=True)
    

    class Meta:
        verbose_name_plural = 'Expenses'
    @property
    def short_description(self):
         return truncatechars(self.description,50)
    def __str__(self):
        return self.name