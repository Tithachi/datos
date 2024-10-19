from django.shortcuts import render, redirect
from .models import *
from .forms import ItemForm, CustomerForm, QuotationItemFormSet, QuotationForm, InvoiceForm, SupplierForm, ExpenseForm
from django.shortcuts import render, redirect,get_object_or_404
from .forms import QuotationForm, QuotationItemFormSet
from .models import Quotation, Item
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from .pdf_utils import generate_quote, generate_invoice
import pandas as pd
from decimal import Decimal
from django.utils import timezone  # For current date and time
import datetime 
from datetime import timedelta
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.db.models import F, Sum, FloatField
from django.db.models.functions import Coalesce
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.conf import settings
from .models import Invoice, QuotationItem  # Adjust the import according to your app structure
from io import BytesIO

def send_invoice_email(request, invoice_id):
    # Fetch the Invoice entry from the database
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Fetch related items and calculate totals (similar to your previous view)
    quotation_items = QuotationItem.objects.filter(quotation=invoice.quotation)
    
    # Create a list of items for the PDF table
    items = []
    for q_item in quotation_items:
        item = q_item.item  # Assuming 'item' is linked to another model with 'description' and 'unit_price' fields
        item_data = {
            "name": f"{item.name}",
            "description": f"{item.description}",
            "rate": f"{item.unit_price:.2f}",
            "qty": str(q_item.quantity),
            "discount": "5.00",  # Example discount value
            "amount": f"{(item.unit_price * q_item.quantity):.2f}",
            "tax": f"{(item.unit_price * q_item.quantity * Decimal(0.16)):.2f}",
        }
        items.append(item_data)
    
    # Calculate totals for the PDF
    subtotal = sum(float(i['amount']) for i in items)
    tax = subtotal * 0.16  # Example 16% tax
    total = subtotal + tax

    # Prepare totals dictionary
    totals = {
        'subtotal': f"ZMW {subtotal:.2f}",
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
        'payment_info': "MTN Money: +260 96 4394236",
        'notes': "datos coming soon..."
    }

    # Client details
    client_details = {
        'name': invoice.quotation.customer.company,
        'email': invoice.quotation.customer.email,
        'phone': invoice.quotation.customer.phone,
        'address': invoice.quotation.customer.address,
    }

    # Invoice receipt info
    receipt_info = {
        'number': invoice.invoice_number,
        'date': invoice.date_created.strftime('%Y-%m-%d'),
        'due_date': invoice.due_date.strftime('%Y-%m-%d'),
    }

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Generate the PDF with actual data
    generate_invoice(
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

    # Create an email message
    email = EmailMessage(
        subject=f"Invoice {invoice.invoice_number}",
        body="Please find attached your invoice.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[invoice.quotation.customer.email,'timothy.chimfwembe@datoscw.com'],
    )

    # Attach the PDF file to the email
    email.attach(f"Invoice_{invoice.invoice_number}.pdf", buffer.getvalue(), 'application/pdf')

    # Send the email
    email.send()

    return HttpResponse("Invoice sent successfully!")



def get_revenue_data(request):
    # Get the current date
    today = datetime.now()

    # Calculate the last 7 days' totals
    revenue_data = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0)
        day_end = day.replace(hour=23, minute=59, second=59)

        # Fetch invoices for the day
        invoices = Invoice.objects.filter(date_created__range=[day_start, day_end])
        daily_total = Decimal('0.00')

        # Loop through invoices and calculate the total
        for invoice in invoices:
            quotation_items = QuotationItem.objects.filter(quotation=invoice.quotation)
            subtotal = sum(item.item.unit_price * item.quantity for item in quotation_items)
            tax = subtotal * Decimal('0.16')  # 16% tax
            total = subtotal + tax
            daily_total += total

        revenue_data.append({
            'day': day.strftime('%Y-%m-%d'),
            'total': float(daily_total)
        })
        
    # Reverse the data so the latest date is on the right
    revenue_data.reverse()

    return JsonResponse(revenue_data, safe=False)


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
            "name": f"{item.name}",
            "description": f"{item.description}",
            "rate": f"{item.unit_price:.2f}",
            "qty": str(q_item.quantity),
            "discount": "5.00",  # Example discount value
            "amount": f"{(item.unit_price * q_item.quantity):.2f}",
            "tax": f"{(item.unit_price * q_item.quantity * Decimal(0.16)):.2f}",

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
        'payment_info': "MTN Money: +260 96 4394236",
        'notes': "datos coming soon..."
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


def view_invoice_pdf(request, entry_id):
    # Fetch the Invoice entry from the database
    invoice = get_object_or_404(Invoice, id=entry_id)

    # Fetch related items (assuming there are related quotation items through the linked quotation)
    invoice_items = QuotationItem.objects.filter(quotation=invoice.quotation)

    # Prepare items data for the PDF
    items = []
    for q_item in invoice_items:
        item = q_item.item  # Assuming 'item' is linked to another model with 'description' and 'unit_price' fields
        item_data = {
            "name": f"{item.name}",
            "description": f"{item.description}",
            "rate": f"{item.unit_price:.2f}",
            "qty": str(q_item.quantity),
            "discount": "5.00",  # Example discount value
            "amount": f"{(item.unit_price * q_item.quantity):.2f}",
            "tax": f"{(item.unit_price * q_item.quantity * Decimal(0.16)):.2f}",
        }
        items.append(item_data)

    # Calculate totals for the PDF
    subtotal = sum(float(i['amount']) for i in items)
    tax = subtotal * 0.16  # Example 16% tax
    total = subtotal + tax
    balance_due = Decimal(total) - invoice.amount_paid

    totals = {
        'subtotal': f"ZMW {subtotal:.2f}",
        'discount': 'ZMW 0.00',  # Example value
        'shipping': 'ZMW 0.00',  # Example value
        'tax': f"ZMW {tax:.2f}",
        'total': f"ZMW {total:.2f}",
        'paid': f"ZMW {invoice.amount_paid:.2f}",
        'balance_due': f"ZMW {balance_due:.2f}",  # Now works without the error
    }

    # Dummy company details (replace with actual details or fetch from DB)
    company_details = {
        'name': "Datos Technology",
        'address': "11586 Teagles Rd, Makeni, Lusaka",
        'email': "info@datoscw.com",
        'phone': "+260 96 4394236",
        'payment_info': "MTN Money: +260 96 4394236",
        'notes': "datos coming soon..."
    }

    # Client details (from the related Quotation model's 'customer' foreign key)
    client_details = {
        'name': invoice.quotation.customer.company,
        'email': invoice.quotation.customer.email,
        'phone': invoice.quotation.customer.phone,
        'address': invoice.quotation.customer.address,
    }

    # Invoice receipt info
    receipt_info = {
        'number': invoice.invoice_number,
        'date': invoice.date_created.strftime('%Y-%m-%d'),
        'due_date': invoice.due_date.strftime('%Y-%m-%d'),
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



def home(request):
    # Fetch all invoices, quotations, and expenses
    invoices = Invoice.objects.all().order_by('-date_created')
    quotations = Quotation.objects.all().order_by('-date_created')
    expenses = Expense.objects.all().order_by('-date')

    # Calculate total for each quotation and store it
    quotation_data = []
    for quotation in quotations:
        quotation_items = QuotationItem.objects.filter(quotation=quotation)
        subtotal = sum(item.item.unit_price * item.quantity for item in quotation_items)
        tax = subtotal * Decimal('0.16')  # Assuming a 16% tax rate
        total = subtotal + tax
        quotation_data.append({'quotation': quotation, 'total': total})

    # Calculate total revenue
    invoice_data = []
    total_revenue = Decimal('0.00')
    for invoice in invoices:
        quotation_items = QuotationItem.objects.filter(quotation=invoice.quotation)
        subtotal = sum(item.item.unit_price * item.quantity for item in quotation_items)
        tax = subtotal * Decimal('0.16')
        total = subtotal + tax
        total_revenue += total
        invoice_data.append({'invoice': invoice, 'total': total})

    # Calculate total expenses
    total_expenses = sum(expense.amount for expense in expenses)

    

    # Get today's and yesterday's dates
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Calculate today's and yesterday's expenses
    today_expenses = sum(expense.amount for expense in Expense.objects.filter(date=today))
    yesterday_expenses = sum(expense.amount for expense in Expense.objects.filter(date=yesterday))

    # Calculate percentage change for expenses
    if yesterday_expenses > 0:
        expenses_percentage_change = ((today_expenses - yesterday_expenses) / yesterday_expenses) * 100
    elif today_expenses > 0:
        expenses_percentage_change = 100.0  # Significant increase if no expenses yesterday
    else:
        expenses_percentage_change = 0.0  # No expenses for both days

    # Ensure the percentage change is absolute
    if expenses_percentage_change < 0:
        expenses_percentage_change = abs(expenses_percentage_change)

    # Determine change status for expenses
    if today_expenses > yesterday_expenses:
        expenses_change_status = 'increase'
    elif today_expenses < yesterday_expenses:
        expenses_change_status = 'decrease'
    else:
        expenses_change_status = 'flat'

    # Calculate today's and yesterday's total revenue
    today_total_revenue = sum(
        item.item.unit_price * item.quantity for item in
        QuotationItem.objects.filter(quotation__invoice__date_created__date=today)
    )
    yesterday_total_revenue = sum(
        item.item.unit_price * item.quantity for item in
        QuotationItem.objects.filter(quotation__invoice__date_created__date=yesterday)
    )

    # Calculate percentage change for revenue
    if yesterday_total_revenue > 0:
        percentage_change = ((today_total_revenue - yesterday_total_revenue) / yesterday_total_revenue) * 100
    elif today_total_revenue > 0:
        percentage_change = 100.0
    else:
        percentage_change = 0.0

    if percentage_change < 0:
        percentage_change = abs(percentage_change)

    # Determine change status for revenue
    if today_total_revenue > yesterday_total_revenue:
        change_status = 'increase'
    elif today_total_revenue < yesterday_total_revenue:
        change_status = 'decrease'
    else:
        change_status = 'flat'
        
    # Calculate profit (Revenue - Expenses)
    profit = today_total_revenue - today_expenses

    # Prepare context to send to the template
    context = {
        'invoice_data': invoice_data,
        'quotation_data': quotation_data,
        'today_total_revenue':today_total_revenue,
        'total_revenue': total_revenue,
        'today_expenses':today_expenses,
        'total_expenses': total_expenses,
        'profit': profit,
        'percentage_change': round(percentage_change, 2),
        'change_status': change_status,
        'expenses_percentage_change': round(expenses_percentage_change, 2),
        'expenses_change_status': expenses_change_status,
    }

    return render(request, 'home.html', context)








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
    quotes = Quotation.objects.all().order_by('-date_created')
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
            return redirect('invoices')  # Redirect after POST to avoid re-submission on refresh
    else:
        form = InvoiceForm()

    # Fetch all invoices
    invoices = Invoice.objects.all().order_by('-date_created')
    
    # Fetch all quotations
    quotations = Quotation.objects.all()

    # Calculate total for each quotation and store it
    quotation_data = []
    for quotation in quotations:
        # Fetch the related quotation items for each quotation
        quotation_items = QuotationItem.objects.filter(quotation=quotation)

        # Calculate the total for the quotation
        subtotal = sum(item.item.unit_price * item.quantity for item in quotation_items)
        tax = subtotal * Decimal('0.16')  # Assuming a 16% tax rate
        total = subtotal + tax

        # Store the quotation data with the total
        quotation_data.append({
            'quotation': quotation,
            'total': total
        })

    # Create a list to store invoice data along with the total amount for each quotation
    invoice_data = []
    for invoice in invoices:
        # Fetch the related quotation items for the invoice's quotation
        quotation_items = QuotationItem.objects.filter(quotation=invoice.quotation)

        # Calculate the total for the quotation linked to this invoice
        subtotal = sum(item.item.unit_price * item.quantity for item in quotation_items)
        tax = subtotal * Decimal('0.16')  # Use Decimal for the tax rate
        total = subtotal + tax

        # Fetch all receipts related to this invoice
        receipts = Receipt.objects.filter(invoice=invoice)

        # Calculate the total amount paid from all receipts
        paid = sum(receipt.amount_received for receipt in receipts)

        # Calculate the balance as total minus the total paid
        balance = total - paid

        # Determine the status based on due_date and paid amount
        current_date = timezone.now().date()  # Get the current date

        # Convert invoice.due_date to date() if it contains time part
        due_date = invoice.due_date.date() if isinstance(invoice.due_date, datetime) else invoice.due_date

        if paid == 0:
            status = 'NOT PAID'
        elif due_date < current_date and paid < total:
            status = 'OVERDUE'
        elif due_date >= current_date and paid < total:
            status = 'PARTIAL'
        else:
            status = 'PAID'

        # Add the invoice details along with the total amount, paid amount, balance, and status to the list
        invoice_data.append({
            'invoice': invoice,
            'total': total,  # Add total amount to the dictionary
            'paid': paid,  # Add total paid amount
            'balance': balance,  # Add balance
            'status': status,
        })

    context = {
        'form': form,
        'invoice_data': invoice_data,  # Passing the invoice data with totals and status
        'quotation_data': quotation_data  # Pass the calculated quotation totals
    }

    return render(request, 'invoice.html', context)




def receipts(request):
    # Fetch all receipts
    receipts = Receipt.objects.all().order_by('-date_received')
    
    # Create a list to store receipt data
    receipt_data = []
    for receipt in receipts:
        invoice = receipt.invoice  # Get the associated invoice
        
        # Add the receipt details along with the total amount and balance to the list
        receipt_data.append({
            'receipt': receipt,
            'invoice': invoice,
            'amount_received': receipt.amount_received,
            'due_date': invoice.due_date,
        })
    
    context = {
        'receipt_data': receipt_data,  # Pass the receipt data to the template
    }
    
    return render(request, 'reciepts.html', context)


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


def dashboard_view(request):
    today = timezone.now().date()  # Get today's date
    date_range = [today - timedelta(days=i) for i in range(7)]  # Create a list for the last 7 days
    
    # List to store total revenue for each of the last 7 days
    daily_totals = []

    for day in date_range:
        # Filter invoices created on the current day
        invoices = Invoice.objects.filter(date_created__date=day)
        total_revenue = Decimal('0.00')  # Initialize total revenue for the current day

        # Calculate total revenue for each invoice on that day
        for invoice in invoices:
            quotation_items = QuotationItem.objects.filter(quotation=invoice.quotation)
            
            # Calculate subtotal and add tax for each invoice
            subtotal = sum(item.item.unit_price * item.quantity for item in quotation_items)
            tax = subtotal * Decimal('0.16')
            total = subtotal + tax
            
            # Add to the day's total revenue
            total_revenue += total

        # Append the day's total revenue to the list
        daily_totals.append(float(total_revenue))  # Convert Decimal to float

    # Reverse to make the most recent day appear last
    daily_totals.reverse()

    # Pass the daily totals to the template as 'profit_data'
    return render(request, 'home.html', {'profit_data': daily_totals})

# Supplier View
def suppliers(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('suppliers')
    else:
        form = SupplierForm()
    
    suppliers = Supplier.objects.all()
    return render(request, 'suppliers.html', {'form': form, 'suppliers': suppliers})

def expenses(request):
    suppliers = Supplier.objects.all()  # Fetching all suppliers
    expenses = Expense.objects.all().order_by('-date')  # Fetching all suppliers
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expenses')  # Adjust to your URL name for listing expenses
    else:
        form = ExpenseForm()

    context = {
        'form': form,
        'expenses': expenses,
        'suppliers': suppliers,  # Pass suppliers to the template
    }

    return render(request, 'expenses.html', context)






