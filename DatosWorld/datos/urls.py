from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('quotes/', views.quotes, name='quotes'),
    path('customers/', views.customers, name='customers'),
    path('invoices/', views.invoices, name='invoices'),
    path('reciepts/', views.receipts, name='reciepts'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('expenses/', views.expenses, name='expenses'),
    path('items/', views.items, name='items'),
    path('view_quote_pdf/<int:entry_id>/', views.view_quote_pdf, name='view_quote_pdf'),
    path('view_invoice_pdf/<int:entry_id>/', views.view_invoice_pdf, name='view_invoice_pdf'),
    path('send_invoice_email/<int:invoice_id>/', views.send_invoice_email, name='send_invoice_email'),
    path('send_quotation_email/<int:quotation_id>/', views.send_quotation_email, name='send_quotation_email'),
    path('get-revenue-data/', views.get_revenue_data, name='get_revenue_data'),
    # path('deleteexpense/<str:pk>/', views.deleteexpense, name='deleteexpense'),
    # path('listincome/', views.listincome, name='listincome'),
    # path('addincome/', views.addincome, name='addincome'),
    # path('updateincome/<str:pk>/', views.updateincome, name='updateincome'),
    # path('deleteincome/<str:pk>/', views.deleteincome, name='deleteincome'),
    # path('invoice/', views.invoice, name='invoice'),
    # path("listIncome/", views.listIncome, name="listIncome"),
    # path("listExpense/", views.listExpense, name="listExpense"),
]