from django.db import models
from django.utils import timezone
import random

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
