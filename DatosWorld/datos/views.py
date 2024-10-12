from django.shortcuts import render, redirect
from .models import *
from .forms import ItemForm, CustomerForm, QuotationItemFormSet, QuotationForm, InvoiceForm
from django.shortcuts import render, redirect,get_object_or_404
from .forms import QuotationForm, QuotationItemFormSet
from .models import Quotation, Item
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from .pdf_utils import generate_quote
import pandas as pd
from decimal import Decimal
from django.utils import timezone  # For current date and time
import datetime 

def view_quote_pdf(request, entry_id):
    # Fetch the Quotation entry from the database
    quotation = get_object_or_404(Quotation, id=entry_id)
    
    # Fetch related items and calculate totals
    quotation_items = QuotationItem.objects.filter(quotation=quotation)
    
    # Create a list of items for the PDF table
    items = []
    for q_item in quotation_items:
        item = q_item.item  # Assuming 'item' is linked to another model with 'description' and 'unit_price' fields
        item_data = {
            "description": f"{item.name}, {item.description}",
            "rate": f"{item.unit_price:.2f}",
            "qty": str(q_item.quantity),
            "tax": "20.00",  # Example tax value
            "discount": "5.00",  # Example discount value
            "amount": f"{(item.unit_price * q_item.quantity):.2f}",
        }
        items.append(item_data)
    
    # Calculate totals for the PDF
    subtotal = sum(float(i['amount']) for i in items)
    tax = subtotal * 0.16  # Example 16% tax
    total = subtotal + tax
    totals = {
        'subtotal': f"ZMW {subtotal:.2f}",
        'discount': 'ZMW 0.00',  # Example value
        'shipping': 'ZMW 0.00',  # Example value
        'tax': f"ZMW {tax:.2f}",
        'total': f"ZMW {total:.2f}",
        'paid': 'ZMW 0.00',  # Example value
        'balance_due': f"ZMW {total:.2f}",
    }
    
    # Dummy company details (replace with actual details or fetch from DB)
    company_details = {
        'name': "Datos Technology",
        'address': "11586 Teagles Rd, Makeni, Lusaka",
        'email': "info@datoscw.com",
        'phone': "+260 96 4394236",
        'payment_info': "Airtel: +260 97 5875598",
        'notes': "Changing Worlds"
    }

    # Client details (from Quotation model's 'customer' foreign key)
    client_details = {
        'name': quotation.customer.company,
        'email': quotation.customer.email,
        'phone': quotation.customer.phone,
        'address': quotation.customer.address,
    }

    # Quotation receipt info
    receipt_info = {
        'number': quotation.quotation_number,
        'date': quotation.date_created.strftime('%Y-%m-%d'),
        'due_date': quotation.expiry_date.strftime('%Y-%m-%d'),
        'created_on': pd.Timestamp.now(),  # Simulating the created_on field for example purposes
    }

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Generate the PDF with actual data
    generate_quote(
        buffer,
        svg_logo_path="C:/Users/Timothy/Desktop/Datos/DatosWorld/static/datos/assets/img/pdf_elements/datosbb.svg",
        company_details=company_details,
        client_details=client_details,
        receipt_info=receipt_info,
        items=items,
        totals=totals,
        watermark_path="C:/Users/Timothy/Desktop/Datos/DatosWorld/static/datos/assets/img/pdf_elements/datos_watermark.png"
    )

    # File pointer goes to the beginning of the buffer
    buffer.seek(0)

    # Return the PDF as a response for viewing in the browser
    return HttpResponse(buffer, content_type='application/pdf')

# Create your views here.
def home(request):
    return render(request, 'home.html')



def quotes(request):
    if request.method == 'POST':
        form = QuotationForm(request.POST)
        formset = QuotationItemFormSet(request.POST)

        # Debugging: Print out request POST data
        print("Request POST data:", request.POST)
        
        print("Quotation Form Valid:", form.is_valid())
        print("Quotation Form Errors:", form.errors)
        print("Formset Valid:", formset.is_valid())
        print("Formset Errors:", formset.errors)

        if form.is_valid() and formset.is_valid():
            # Save the Quotation instance first
            quotation = form.save()
            
            # Save items related to the quotation
            for item_form in formset:
                if item_form.is_valid() and item_form.cleaned_data:
                    quotation_item = item_form.save(commit=False)
                    quotation_item.quotation = quotation
                    quotation_item.save()

            return redirect('quotes')

    else:
        form = QuotationForm()
        formset = QuotationItemFormSet(queryset=QuotationItem.objects.none())  # Empty formset for new data

    # Fetch all quotations and items
    quotes = Quotation.objects.all()
    items = Item.objects.all()

    context = {
        'form': form,
        'formset': formset,
        'quotes': quotes,
        'items': items,
    }
    return render(request, 'quotes.html', context)


def customers(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customers')  # Redirect after POST to avoid re-submission on refresh
    else:
        form = CustomerForm()

    customers = Customer.objects.all()  # Fetch all items to display in the table
    context = {
        'form': form,
        'customers': customers
    }
    return render(request, 'customers.html', context)

def invoices(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('invoice')  # Redirect after POST to avoid re-submission on refresh
    else:
        form = InvoiceForm()

    # Fetch all invoices
    quotes = Quotation.objects.all()
    invoices = Invoice.objects.all()

    # Create a list to store invoice data along with total amount for each quotation
    invoice_data = []

    for invoice in invoices:
        # Fetch the related quotation items for the invoice's quotation
        quotation_items = QuotationItem.objects.filter(quotation=invoice.quotation)

        # Calculate the total for the quotation linked to this invoice
        subtotal = sum(item.item.unit_price * item.quantity for item in quotation_items)
        tax = subtotal * Decimal('0.16')  # Use Decimal for the tax rate
        total = subtotal + tax

        # Determine the status based on due_date and amount paid
        current_date = timezone.now().date()  # Get the current date

        # Convert invoice.due_date to date() if it contains time part
        due_date = invoice.due_date.date() if isinstance(invoice.due_date, datetime.datetime) else invoice.due_date

        if due_date < current_date and invoice.amount_paid < total:
            status = 'OVERDUE'
        elif due_date >= current_date and invoice.amount_paid < total:
            status = 'PARTIAL'
        else:
            status = 'PAID'

        # Add the invoice details along with the total amount and status to the list
        invoice_data.append({
            'invoice': invoice,
            'total': total,  # Add total amount to the dictionary
            'status': status,  # Add the calculated status
            "quotes":quotes
        })

    context = {
        'form': form,
        'invoice_data': invoice_data,  # Passing the invoice data with totals and status
    }

    return render(request, 'invoice.html', context)


def reciepts(request):
    return render(request, 'reciepts.html')

def items(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('items')  # Redirect after POST to avoid re-submission on refresh
    else:
        form = ItemForm()

    items = Item.objects.all()  # Fetch all items to display in the table
    context = {
        'form': form,
        'items': items
    }
    return render(request, 'items.html', context)

def suppliers(request):
    return render(request, 'suppliers.html')


def addcustomer(request):
    form = CustomerForm()
    customer = Customer.objects.all()

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return redirect('customers')

    context = {'form': form, 'customer': customer}
    return render(request, 'customers.html', context)





