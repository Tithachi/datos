from django.shortcuts import render, redirect
from .models import *
from .forms import ItemForm, CustomerForm, QuotationItemFormSet, QuotationForm
from django.shortcuts import render, redirect
from .forms import QuotationForm, QuotationItemFormSet
from .models import Quotation, Item
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

def render_to_pdf(template_scr, context_dict={}):
    template = get_template(template_scr)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None 

data={
    "company":"Ndetelako",
    "address":"11586 Teagles Rd Makeni",
    "city":"Lusaka",
    "state":"Lusaka",
    "zipcode":"10101",
    "phone":"260 96 4394236",
    "email":"thapelochimfwembe@gmail.com",
    "website":"datos.world" 
    }

class ViewPDFQuote(View):
    
    def get(self, request, *arge, **kwargs):
        
        pdf = render_to_pdf('quotepdf.html', data)
        return HttpResponse(pdf,content_type='application/pdf')

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
    return render(request, 'invoice.html')

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





