from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('quotes/', views.quotes, name='quotes'),
    path('customers/', views.customers, name='customers'),
    path('invoices/', views.invoices, name='invoices'),
    path('reciepts/', views.reciepts, name='reciepts'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('items/', views.items, name='items'),
    path('viewpdfquote/', views.ViewPDFQuote.as_view(), name='viewpdfquote')
    # path('deleteexpense/<str:pk>/', views.deleteexpense, name='deleteexpense'),
    # path('listincome/', views.listincome, name='listincome'),
    # path('addincome/', views.addincome, name='addincome'),
    # path('updateincome/<str:pk>/', views.updateincome, name='updateincome'),
    # path('deleteincome/<str:pk>/', views.deleteincome, name='deleteincome'),
    # path('invoice/', views.invoice, name='invoice'),
    # path("listIncome/", views.listIncome, name="listIncome"),
    # path("listExpense/", views.listExpense, name="listExpense"),
]